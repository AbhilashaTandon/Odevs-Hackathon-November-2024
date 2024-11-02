from typing import Tuple
import requests

OCEAN = 0
OUTSIDE_FLORIDA = 1

"""Florida
Northernmost point(31°00′04″N) 85°09′52″W  Alabama border north of Malone
Southernmost point(24°31′16″N) 81°57′49″W  Ballast Key in the Mule Keys
Easternmost point   26°46′43″N(80°01′52″W)   Palm Beach Shores
Westernmost point   30°51′59″N(87°38′06″W)   Alabama border on the Perdido River west of Walnut Hill

31.00111111 N - 24.52111111 N
80.03111111 W - 87.635 W
"""

FLORIDA_NORTH = 31.001111111
FLORIDA_SOUTH = 24.521111111
FLORIDA_EAST = -80.031111111
FLORIDA_WEST = -87.635000000


def get_tract(lon: float, lat: float) -> Tuple[int, int]:
    """returns block fips of census tract for given latitude and longitude in florida

    Args:
        lat (_type_): latitude
        lon (_type_): longitude

    Returns:
        Tuple[int, int]: first is county code, second is census tract code
        if county code is 0 it is ocean, if county code is 1 it is outside florida
    """
    #
    link = 'https://geo.fcc.gov/api/census/area?lat={0}&lon={1}&format=json'.format(
        lat, lon)
    response = requests.get(link).json()

    # print(response)

    if (len(response['results']) == 0):
        return (OCEAN, 0)
    if (int(response['results'][0]['state_fips']) != 12):  # if not florida
        return (OUTSIDE_FLORIDA, 0)
    else:
        fips = response['results'][0]['block_fips']
        # state = fips[:2]
        # state is always florida
        county = fips[2:5]
        tract = fips[5:11]
        return int(county), int(tract)
        # block fips is 15 digits, is fips of census block
        # first 11 digits are just census tract


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
