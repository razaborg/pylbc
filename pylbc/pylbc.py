#!/usr/bin/env python3
import requests
import time
import datetime
import json

CATEGORIES = { 8: 'immobilier', 9: 'ventes', 10:'locations', 11: 'colocations'}
get_cat_by_id = lambda x : next((name for id,name in CATEGORIES.items() if str(id) == str(x)), False)
get_cat_by_name = lambda x : next((str(id) for id,name in CATEGORIES.items() if name == x), False)
check_cat_name = lambda x : True if x in CATEGORIES.values() else False
check_cat_id = lambda x : True if x in CATEGORIES.keys() else False

REAL_ESTATE_TYPES = {
        1: 'maison',
        2: 'appartement',
        3: 'terrain',
        4: 'parking',
        5: 'autre'
        }
get_type_by_id = lambda x : next((name for id,name in REAL_ESTATE_TYPES.items() if id == x), False)
get_type_by_name = lambda x : next((str(id) for id,name in REAL_ESTATE_TYPES.items() if name == x), False)
check_type_name = lambda x : True if x in REAL_ESTATE_TYPES.values() else False
check_type_id = lambda x : True if x in REAL_ESTATE_TYPES.keys() else False


DEPARTMENTS = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '2A', '2B', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '971', '972', '973', '974', '976')

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
        
        self.__category = {'id': get_cat_by_name('immobilier')} # by default all "IMMOBILIER" ads
        self.__range_filters = {
                "rooms": {},
                "square": {},
                "price": {}
                }
        self.__enum_filters = {
                'real_estate_type': [],
                'ad_type': ['offer'] # default to "offers"
                }
        self.__location_filters = {
                "area":{"lat":0.0,"lng":0.0,"radius":0},
                "city_zipcodes":[],
                "departments":[],
                "disable_region":True,
                "locations": [],
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
    
    def set_query(self, query, titleonly=False):
        '''
        Define a list of keywords (a query) to filter the results
        If titleonly is set to true, set the option "rechercher dans le titre uniquement"

        Compatible with leboncoin special operators:
            "this word" : to output only results containing exactly 'this word'
            NOT word: to output only results NOT containing 'word'
            this OR that: to output results containing 'this' or 'that'
            () : to group and priorise keywords
        '''

        if titleonly:
            self.__keywords['type'] = 'subject'
        self.__keywords['text'] = query

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
        if not check_cat_name(name) :
           raise InvalidCategory
        self.__category['id'] = get_cat_by_name(name)
    
    def add_city(self, cityname, zipcode):
        '''
        Allow to add a new citiy where we want to search
        '''
        # WARNING: not compatible with departments list! Need to clear it first.
        self.__location_filters['departments'] = []
        self.__location_filters['locations'].append({"city":cityname,"zipcode":zipcode,"locationType":"city"})


    def set_real_estate_types(self, list_of_types):
        '''
        Define the list real estate types we are looking for.
        '''
        self.__enum_filters['real_estate_type'] = []
        for name in list_of_types:
            if not check_type_name(name):
                raise InvalidEstateType
            self.__enum_filters['real_estate_type'].append(get_type_by_name(name))

    def set_departments(self, list_of_departments):
        '''
        Define a list of departments to search into.
        Incompatible with coordinates search.
        '''
        # WARNING: not compatible with locations list (cities typically)! Need to clear it first.
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
        print(self.payload)
    
    def request_once(self, verify=True):
        '''
        Requests only one result page and returns the result of the API.
        '''
        self.__prepare_payload()
        req = self.session.post(self.api_url, data=json.dumps(self.payload), headers=self.headers, verify=verify)
        if not req.status_code == requests.codes.ok:
            req.raise_for_status()
        return json.loads(req.text)
    def request_infos(self, verify=True):
        '''
        Requests only the metadata of the query and returns the result.
        '''
        self.__disable_results()
        req = self.session.post(self.api_url, data=json.dumps(self.payload), headers=self.headers, verify=verify)
        self.__enable_results()
        if not req.status_code == requests.codes.ok:
            req.raise_for_status()
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
                yield SearchResult.from_dict(result)


class SearchResult():
    '''
    This object handles Results from the lbc API.
    This is a lighter version of the returned object, with only the needed elements \
    and some useful methods.
    '''
    def __init__(self, title, category, publication_date, price, coordinates, real_estate_type, square, url, thumbnail):
        self.title = title
        self.publication_date = publication_date
        self.category = category
        self.price = price
        self.coordinates = coordinates
        self.real_estate_type = real_estate_type
        self.square = square 
        self.url = url
        self.thumbnail = thumbnail

    @classmethod
    def from_dict(cls, result):
        assert(type(result) is type(dict()))
        # check that all the required keys are present in the dict
        REQUIRED_KEYS = ('first_publication_date', 'subject', 'url', 'price', 'images', \
                'attributes', 'location', 'category_id')
        assert(all([key in result.keys() for key in REQUIRED_KEYS]))

        ts = time.mktime(time.strptime(result['first_publication_date'], '%Y-%m-%d %H:%M:%S'))
        publication_date = datetime.date.fromtimestamp(ts) 
        
        title = result['subject']
        url = result['url']
        category = get_cat_by_id(result['category_id'])
        
        if len(result['price']) == 1:
            price = result['price'][0]
        else:
            price = str(result['price'])
        
        if 'thumb_url' in result['images']:
            thumbnail = result['images']['thumb_url']
        else:
            thumbnail = ''

        assert('lat' in result['location'].keys() and \
                'lng' in result['location'].keys())
        
        coordinates = (result['location']['lat'], result['location']['lng'])
        
        real_estate_type = None
        square = None
        for i in result['attributes'] :
            key = i['key']
            if key == 'real_estate_type':
                real_estate_type = i['value_label'].lower()
            if key == 'square':
                square = i['value'].lower()
        
        return cls(title, category, publication_date, price, coordinates, real_estate_type, square, url, thumbnail)

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
        CUSTOM METHOD
        Check if the ad is about an appartement or not 
        '''
        if self.real_estate_type == 'appartement':
            return True
        else:
            return False
        
    def is_recent(self, days=5):
        '''
        CUSTOM METHOD
        Check if the ad can be considered as "recent".
        The default recent ads are the ones < 5 days.
        '''
        now = datetime.date.fromtimestamp(time.time())
        delta = now - self.publication_date
        if delta.days <= int(days):
            return True
        else:
            return False
    
    def price_per_square(self):
        '''
        CUSTOM METHOD
        Return the price per m2 of a result.
        '''
        return self.price/self.square

    def __repr__(self):
        s = 'SearchResult(title="{}", category="{}", publication_date="{}", price={}, coordinates={}, real_estate_type="{}", square={}, url="{}", thumbnail="{}")'.format( \
                self.title,
                self.category,
                self.publication_date,
                self.price,
                self.coordinates,
                self.real_estate_type,
                self.square,
                self.url,
                self.thumbnail
                )
        return s



