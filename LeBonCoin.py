#!/usr/bin/env python3
import requests
import time
import requests
import datetime
import pprint
import json
from raw_values import *
from collections import namedtuple
import time
import datetime



class Search():
    '''
    This object handles the interface with the lbc search API.
    It provides useful methods to make requests using Python and process results.
    '''
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
            #for i in result['attributes'] :
            #    result[i['key']] = {'value': i['value'], 'value_label': i ['value_label']}
            #del result['attributes']
            #out.append(namedtuple("Result", result.keys())(*result.values()))
            out.append(SimplifiedResult(result))
        return out


class SimplifiedResult():
    '''
    This object handles Results from the lbc API.
    This is a lighter version of the returned object, with only the needed elements \
    and some useful methods.
    '''
    def __init__(self, result):
        assert(type(result) is type(dict()))
        # check that all the required keys are present in the dict
        
        REQUIRED_KEYS = ('first_publication_date', 'subject', 'url', 'price', 'images', \
                'attributes', 'location', 'category_id')
        assert(all([key in result.keys() for key in REQUIRED_KEYS]))

        ts = time.mktime(time.strptime(result['first_publication_date'], '%Y-%m-%d %H:%M:%S'))
        self.publication_date = datetime.date.fromtimestamp(ts)
        now = datetime.date.fromtimestamp(time.time())
        delta = now - self.publication_date
        if delta.days < 5:
            self.is_recent = True
        else:
            self.is_recent = False
        
        self.title = result['subject']
        self.url = result['url']
        
        if len(result['price']) == 1:
            self.price = result['price'][0]
        else:
            self.price = str(result['price'])
        
        if 'thumb_url' in result['images']:
            self.thumbnail = result['images']['thumb_url']
        else:
            self.thumbnail = ''

        assert('lat' in result['location'].keys() and \
                'lng' in result['location'].keys())
        
        self.coordinates = (result['location']['lat'], result['location']['lng'])
        
        self.real_estate_type = None
        self.square = None
        for i in result['attributes'] :
            key = i['key']
            if key == 'real_estate_type':
                self.real_estate_type = i['value_label'].lower()
            if key == 'square':
                self.square = i['value'].lower()
        
        if self.real_estate_type == 'maison':
            self.is_house = True
        else:
            self.is_house = False

        if self.real_estate_type == 'appartement':
            self.is_appartment = True
        else:
            self.is_appartment = False
    


    def __repr__(self):
        s = 'Result(title="{}", is_recent={}, publication_date="{}", price={}, coordinates={}, real_estate_type="{}", square={}, is_house={}, is_appartment={}, url="{}", thumbnail="{}")'.format( \
                self.title,
                self.is_recent,
                self.publication_date,
                self.price,
                self.location,
                self.real_estate_type,
                self.square,
                self.is_house,
                self.is_appartment,
                self.url,
                self.thumbnail)
        return s



