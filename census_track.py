import urllib
import json
import requests

OCEAN = 0
OUTSIDE_FLORIDA = 1


def get_tract(lat, lon) -> int:
    # returns block fips of census track for given latitude and longitude in florida
    link = 'https://geo.fcc.gov/api/census/area?lat={0}&lon={1}&format=json'.format(
        lat, lon)
    response = requests.get(link).json()

    print(response)

    if (len(response['results']) == 0):
        return OCEAN
    if (int(response['results'][0]['state_fips']) != 12):  # if not florida
        return OUTSIDE_FLORIDA
    else:
        return int(response['results'][0]['block_fips'][:11])
        # block fips is 15 digits, is fips of census block
        # first 11 digits are just census track


'''
sample api output

{
  "input": {
    "lat": 40.748333333333335,
    "lon": -73.98527777777778,
    "censusYear": "2020"
  },
  "results": [
    {
      "block_fips": "360610076001001",
      "bbox": [
        -73.988038,
        40.747773,
        -73.98456,
        40.749772
      ],
      "county_fips": "36061",
      "county_name": "New York County",
      "state_fips": "36",
      "state_code": "NY",
      "state_name": "New York",
      "block_pop_2020": 1170,
      "amt": "AMT001",
      "bea": "BEA010",
      "bta": "BTA321",
      "cma": "CMA001",
      "eag": "EAG701",
      "ivm": "IVM001",
      "mea": "MEA002",
      "mta": "MTA001",
      "pea": "PEA001",
      "rea": "REA001",
      "rpc": "RPC001",
      "vpc": "VPC001"
    }
  ]
}'''
