#!/usr/bin/env python3
import requests
import time
import requests
import datetime
import pprint
import json
from raw_values import *
from collections import namedtuple

def LoadResultObj(result):
    return namedtuple("Result", result.keys())(*result.values())

class Search():
    def __init__(self):
        self.api_url = 'https://api.leboncoin.fr/api/adfinder/v1/search'
        self.timestamp = datetime.date.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'LBC;Android;6.0;Android SDK built for x86;phone;616a1ca77ca70180;wwan;4.30.4.0;70400;3', 
            'api_key': 'ba0c2dad52b3ec',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        self.__category = {'id': CATEGORIES['immobilier']} # by default all "IMMOBILIER" ads
        self.__range_filters = {
                "rooms": {},
                "square": {},
                "price": {}
                }
        self.__enum_filters = {
                'real_estate_type': [],
                'ad_type': [AD_TYPES['offres']] # default to "offers"
                }
        self.__location_filters = {
                "area":{"lat":0.0,"lng":0.0,"radius":0},
                "city_zipcodes":[],
                "departments":[],
                "disable_region":True,
                "locations":[],
                "regions":[]
                }
        self.__owner = {}
        self.__limit_alu = 1 # When set to 0, results won't be send by the server, only metrics
        self.__limit = 100 # Maximum results shown in a response. Maximum is 100.
        self.__pivot = "0,0,0" # Used for pagination. The pivot is the Item identifier from which to start the response
        # the pivot is given by the server when number of results exceed the limit of results.
        self.__keywords = {"type":"all"}

    def __prepare_payload(self):
        '''
        Prepare the final payload with the current value of the different variables.
        '''
        self.payload = {
            'pivot' : self.__pivot,
            'limit' : self.__limit,
            'limit_alu' : self.__limit_alu,
            'filters' : {
                'category' : self.__category,
                'enums' : self.__enum_filters,
                'ranges' : self.__range_filters,
                'location' : self.__location_filters,
                'keywords' : self.__keywords,
                'owner' : self.__owner
                },
            "sort_by":"time",
            "sort_order":"desc"
            }

    def set_category(self, name):
        if name not in CATEGORIES.keys():
           raise InvalidCategory
        self.__category['id'] = CATEGORIES[name]

    def set_real_estate_types(self, list_of_types):
        self.__enum_filters['real_estate_type'] = []
        for name in list_of_types:
            if name not in REAL_ESTATE_TYPES.keys():
                raise InvalidEstateType
            self.__enum_filters['real_estate_type'].append(REAL_ESTATE_TYPES[name])

    def set_departments(self, list_of_departments):
        self.__location_filters['locations'] = []
        self.__location_filters['departments'] = []
        for number in list_of_departments:
            number = str(number)
            if number not in DEPARTMENTS:
                raise InvalidDepartment
            dep = { "department_id": number,
                    # "region_id": "6", # This is optionnal., the request works fine with only the department_id
                    "locationType": "department"
                    }
            self.__location_filters['departments'].append(number)
            self.__location_filters['locations'].append(dep)
        self.__location_filters['disable_region'] = False

    def set_rooms(self, mini=None, maxi=None):
        self.__range_filters['rooms'] = self.__set_range(mini, maxi)

    def set_square(self, mini=None, maxi=None):
        self.__range_filters['square'] = self.__set_range(mini,maxi)

    def set_price(self, mini=None, maxi=None):
        self.__range_filters['price'] = self.__set_range(mini, maxi)

    def __disable_results(self):
        '''
        Disable the results in teh response. Will  only return metadata.
        '''
        self.__limit_alu = 0
        self.__limit = 0
        self.__prepare_payload()

    def __enable_results(self):
        '''
        Enable the results in teh response.
        '''
        self.__limit_alu = 1
        self.__limit = 100
        self.__prepare_payload()

    @staticmethod
    def __set_range(mini=None, maxi=None):
        '''
        Static method to process filters of type "range".
        '''

        if maxi and mini:
            assert(maxi > mini)
        if mini:
            assert(mini >= 0)
        if maxi:
            assert(maxi > 0)

        therange = {}
        if mini:
            therange['min'] = mini
        if maxi:
            therange['max'] = maxi
        return therange

    def show_filters(self):
        '''
        Display the current value of the differents filters which have been set
        '''
        self.__prepare_payload()
        pp = pprint.PrettyPrinter(indent=4, compact=False)
        pprint.pprint(self.payload)
    
    def request_once(self, verify=True):
        '''
        Requests only one result page and returns the result of the API.
        '''
        self.__prepare_payload()
        req = self.session.post(self.api_url, data=json.dumps(self.payload), headers=self.headers, verify=verify)
        return json.loads(req.text)

    def request_infos(self, verify=True):
        '''
        Requests only the metadata of the query and returns the result.
        '''
        self.__disable_results()
        req = self.session.post(self.api_url, data=json.dumps(self.payload), headers=self.headers, verify=verify)
        self.__enable_results()
        return json.loads(req.text)

    def iter_results(self, verify=True):
        '''
        Iterates over the pages to get all the results from the API.
        '''

        while True:
            response = self.request_once(verify)
            if not 'ads' in response.keys():
                break
            if 'pivot' in response.keys():
                self.__pivot = response['pivot']
            data = self.__listOfResults2Obj(response['ads'])
            yield data
    
    @staticmethod
    def __listOfResults2Obj(results):
        assert(len(results) > 1)
        out = []
        for result in results:
            for i in result['attributes'] :
                result[i['key']] = {'value': i['value'], 'value_label': i ['value_label']}
            del result['attributes']
            out.append(namedtuple("Result", result.keys())(*result.values()))
        return out
        
