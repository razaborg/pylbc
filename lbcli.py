#!/usr/bin/env python3
import argparse
import pylbc
from raw_values import * 

parser = argparse.ArgumentParser()
parser.add_argument("--coordinates", '-c', nargs=2, metavar=('LAT', 'LNG'), type=float, help='Lat/Long of the center point.')
parser.add_argument('--radius', type=int, help="Radius around the center point.", default=50)
parser.add_argument('--category', '-C', type=str, choices=CATEGORIES.keys(), required=True)
parser.add_argument('--real-estate-type', '-T', type=str, choices=REAL_ESTATE_TYPES.keys(), required=True)
parser.add_argument('--price-range', '-p', nargs=2, type=int)
parser.add_argument('--square-range', '-s', nargs=2, type=int)
parser.add_argument('--rooms-range', '-r', nargs=2, type=int)
parser.add_argument('--m2price', '-m', nargs=2, type=int, metavar=('MAX_PRICE', 'MAX_M2PRICE'), help="Automatically define minimum square size to have a maximum price per m2 < MAX_PRICE.")
parser.add_argument('--order-by', choices=('price', 'time'), default='time')
parser.add_argument('--sort-order', choices=('asc', 'desc'), default='desc')
parser.add_argument('--verbose', '-v', action='store_true')
parser.add_argument('-y', help='Do not ask before printing the results.', action='store_true')
args = parser.parse_args()

query = pylbc.Search()
query.set_category(args.category)
query.set_real_estate_types([args.real_estate_type])

if args.coordinates:
    query.set_coordinates(lat=args.coordinates[0], lng=args.coordinates[1], radius=args.radius)

if args.price_range:
    query.set_price(mini=args.price_range[0], maxi=args.price_range[1])
if args.rooms_range:
    query.set_rooms(mini=args.rooms_range[0], maxi=args.rooms_range[1])
if args.square_range:
    query.set_square(mini=args.square_range[0], maxi=args.square_range[1])

if args.m2price:
    query.set_max_m2price(max_price=args.m2price[0], max_m2price=args.m2price[1])

if args.order_by or args.sort_order:
    query.set_sorting(args.order_by, args.sort_order)

if args.verbose:
    query.show_filters()

infos = query.request_infos()
print("{} results found matching your query.".format(infos['total']))
if not args.y:
    input('Press any key to continue or hit "Ctrl-C" to quit:')
for result in query.iter_results():
    print(result)
