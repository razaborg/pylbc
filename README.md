# lbc_api

Une API Python3 pour LeBonCoin.

## Requirements 

```
pip3 install requests
```

## Usage 

See **main.py** and examples below :-)

## Documentation

Tout se passe autour de la classe **Search()**.

Cette classe dispose de plusieurs méthodes permettant de faciliter la construction des requêtes de recherche.
Pour le moment, seule la fonctionnalité de recherche est visée par cette API, et tout particulièrement la catégorie "immobilier". A l'avenir, peut-être de nouvelles catégories/fonctionnalités de l'API y seront ajoutées.

### Présentation

Plusieurs fonctionnaliéts de recherche sont proposés par le site leboncoin.

Parmi lesquelles :

- définir une catégorie : la méthode **set\_category()**
- définir un fourchette de prix : la méthode **set\_price()**
- définir une fourchette de surface : la méthode **set\_square()**
- définir une fourchette de pièces : la méthode **set\_rooms()**
- définir un/des type de bien : la méthode **set\_real\_estate\_type()**
- définir un/des départements géographiques : la méthode **set\_departments()**
- et concernant cette API c'est tout pour le moment...

Une fois la recherche paramétrée, la requete peut être lancée avec :

- la méthode **request_infos()** pour ne récupérer que les métadonnées des résultats
- la méthode **request_once()** pour charger une seule page de résultats
- la méthode **iter_results()** pour charger l'ensemble des résultats à travers un itérateur

### Examples 

```python
#!/usr/bin/env python3
from LeBonCoin import *

query = LeBonCoin.Search()

query.set_price(mini=500, maxi=900)
query.set_category('locations')
query.set_real_estate_types(['maison'])
query.set_departments(['35'])
# affichage de la requete avant envoi
query.show_filters() 

# pré-requête pour récupérer les métadonnées
infos = query.request_infos()
print(infos)
print("A total of %d results is announced by the server." % infos['total'])

# récupération de tous les résultats
results = []
for items in query.iter_results():
    results.extend(items)
print("%d results have been successfully downloaded." % len(results))
```



