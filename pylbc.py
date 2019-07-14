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
        self.__sort_by = 'time'
        self.__sort_order = 'desc'
        self.coordinates = None

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
            "sort_by":self.__sort_by,
            "sort_order":self.__sort_order
            }

    def set_sorting(self, by, order='desc'):
        CRITERIAS = ('time', 'price')
        ORDERS = ('asc', 'desc')
        assert(by in CRITERIAS)
        assert(order in ORDERS)

        self.__sort_order=order
        self.__sort_by=by

    def set_category(self, name):
        '''
        Define one category to look into.
        '''
        if name not in CATEGORIES.keys():
           raise InvalidCategory
        self.__category['id'] = CATEGORIES[name]

    def set_real_estate_types(self, list_of_types):
        '''
        Define the list real estate types we are looking for.
        '''
        self.__enum_filters['real_estate_type'] = []
        for name in list_of_types:
            if name not in REAL_ESTATE_TYPES.keys():
                raise InvalidEstateType
            self.__enum_filters['real_estate_type'].append(REAL_ESTATE_TYPES[name])

    def set_departments(self, list_of_departments):
        '''
        Define a list of departments to search into.
        Incompatible with coordinates search.
        '''
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

        self.has_departments = True
        self.has_coordinates = False
    
    
    def set_coordinates(self, lat, lng, radius):
        '''
        Define base coordinates and a radius to search around.
        Incompatible with departments search.
        '''
        assert(int(radius) < 100)
        self.__location_filters['locations'] = []
        self.__location_filters['departments'] = []

        self.__location_filters["area"] = { 
            "lat":float(lat), 
            "lng":float(lng), 
            "radius":int(radius)*1000
            }
        self.__location_filters['disable_region'] = False

        self.has_departments = False
        self.coordinates = self.__location_filters["area"]
        self.has_coordinates = True
        
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
        else:
            therange['min'] = 0

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
                break # we exit the loop only when there is no results pages left
            
            if 'pivot' in response.keys():
                self.__pivot = response['pivot']
                # pivot is the last ads id of the page. it is necessary to handle pagination
            
            for result in response['ads']:
                yield SimplifiedResult(result)


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

    def is_house(self): 
        '''
        Check if the ad is about a house or not 
        '''
        if self.real_estate_type == 'maison':
            return True
        else:
            return False

    def is_appartment(self):
        '''
        Check if the ad is about an appartement or not 
        '''
        if self.real_estate_type == 'appartement':
            return True
        else:
            return False
        
    def is_recent(self, days=5):
        '''
        Check if the ad can be considered as "recent".
        The default recent ads are the ones < 5 days.
        '''
        now = datetime.date.fromtimestamp(time.time())
        delta = now - self.publication_date
        if delta.days <= int(days):
            return True
        else:
            return False
    


    def __repr__(self):
        s = 'Result(title="{}", is_recent={}, publication_date="{}", price={}, coordinates={}, real_estate_type="{}", square={}, is_house={}, is_appartment={}, url="{}", thumbnail="{}")'.format( \
                self.title,
                self.is_recent(),
                self.publication_date,
                self.price,
                self.coordinates,
                self.real_estate_type,
                self.square,
                self.is_house(),
                self.is_appartment(),
                self.url,
                self.thumbnail
                )
        return s



