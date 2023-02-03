import requests_cache
import pdb
import json

with open("auth.json") as f:
    headers = json.load("auth.json")

places = {
    "KITSAP": 1231,
    "SKAGIT": 1236,
    "WA": 46,
    "UT": 52,
    "USA": 1,
}

session = requests_cache.CachedSession("inat")

def get_my_obervations(placename):
    url2 = "https://api.inaturalist.org/v1/observations"

    params2 = {
        "verifiable": "true",
        "order_by": "obervations.id",
        "order": "desc",
        "user_id": "mylodon",
        "place_id": places[placename],
        "locale": "en-US",
        "preferred_place_id": 1,
        "per_page": 24,
        "page": 1,
    }
    r = session.get(url2, params=params2, headers=headers)
    data = r.json()
    pages = 1
    result_count = data['total_results']
    per_page = data['per_page']
    observations = dict([(row['taxon']['id'], row) for row in data['results']])
    while pages * per_page < result_count:
        pages += 1
        params2['page'] = pages
        r = session.get(url2, params=params2, headers=headers)
        data = r.json()
        for row in data['results']:
            observations[row['taxon']['id']] = row

    return observations


def get_kitsap_species():
    return get_species("KITSAP")

def get_species(placename):
    url = "https://api.inaturalist.org/v1/observations/species_counts"

    params = {
        "verifiable": "true",
        "spam": "false",
        "place_id": places[placename],
        "locale": "en-US",
        "preferred_place_id": 1,
        "page": 1,
    }
    r = session.get(url, params=params, headers=headers)

    data = r.json()
    results = [row for row in data['results']]
    result_count = data['total_results']
    per_page = data['per_page']
    pages = 1

    while pages * per_page < result_count:
        pages += 1
        params['page'] = pages
        r = session.get(url, params=params, headers=headers)
        data = r.json()
        results.extend([row for row in data['results']])

    return results

def get_unfound(unfound_at_placename, found_placename):
    results = get_species(unfound_at_placename)
    my_observations = get_my_obervations(found_placename)

    for row in results:
        x = ""
        if row['taxon']['id'] not in my_observations:
            print("%s,%s,%s" % (row['taxon']['name'], row["taxon"].get('preferred_common_name', ''), row['count']))


def main():
    placename = "SKAGIT"
    results = get_species(placename)
    my_observations = get_my_obervations(placename)

    max_name_length = 0
    i = 1
    for row in results:
        max_name_length = max(max_name_length, len(row['taxon']['name']))
    for row in results:
        x = ""
        if row['taxon']['id'] in my_observations:
            x = "*"
        else:
            print("%s,%s,%s" % (row['taxon']['name'], row["taxon"].get('preferred_common_name', ''), row['count']))
            #print(row['taxon']['name'] + " " + x)
            #print("%s %s %s %s" % (i, row['taxon']['name'].ljust(max_name_length), row['count'], x))
        i += 1

    #print(json.dumps(data, indent=2))



get_unfound("UT", "USA")
