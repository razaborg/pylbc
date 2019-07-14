#!/usr/bin/env python3
import pylbc

query = pylbc.Search()

query.set_price(mini=500, maxi=900)
query.set_category('locations')
query.set_real_estate_types(['maison'])
query.set_departments(['35'])

#query.show_filters()
infos = query.request_infos()
print(infos)
print("A total of %d results is announced by the server." % infos['total'])

results = []
for item in query.iter_results():
    print(item)


