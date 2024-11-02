# api for cdc social vulnerability index

import pandas as pd

data = pd.read_csv("raw/CDC SVI/Florida.csv")


'''
HBURD Housing cost-burdened occupied housing units with annual income less than $75,000 
DISABL Percentage of civilian noninstitutionalized population with a disability
MUNIT Housing in structures with 10 or more units
MOBILE Mobile homes
CROWD At household level (occupied housing units), more people than rooms
NOVEH Households with no vehicle available
GROUPQ Persons in group quarters estimate
'''


def get_row(county_id: str, tract_id: str):
    fips = int("12" + county_id + tract_id)  # 12 is florida
    rows = data[data['FIPS'] == fips]

    if (len(rows) == 0):
        raise Exception("No rows found.")
    elif (len(rows) > 1):
        raise Exception("Multiple rows found.")
    return rows.iloc[0]


def get_metric(county_id: str, tract_id: str, metric: str, percentile=False):
    """Returns metric in census tract

    Args:
        county_id (str): numerical id of county as string
        tract_id (str): numerical id of census tract as string, only digits
        metric (str): string representing metric to query, must be one of following:
            HBURD Housing cost-burdened occupied housing units with annual income less than $75,000 
            DISABL Percentage of civilian noninstitutionalized population with a disability
            MUNIT Housing in structures with 10 or more units
            MOBILE Mobile homes
            CROWD At household level (occupied housing units), more people than rooms
            NOVEH Households with no vehicle available
            GROUPQ Persons in group quarters estimate
        percentile (bool, optional): whether to get actual value or percentile of tract. Defaults to False.

    Returns:
        (float, float): returns percentage disability or percentile percentage disability, and percent margin of error
    """
    row = get_row(county_id, tract_id)
    estimate = row["EPL_" + metric] if percentile else row['EP_' + metric]
    return estimate,  row['MP_' + metric]


print(get_row("069", "030702")['RPL_THEME4'])
