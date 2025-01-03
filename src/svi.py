# api for cdc social vulnerability index

from collections import Counter
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

data = pd.read_csv("raw/CDC SVI/Florida.csv")

unique_counties = sorted(list(set(data['COUNTY'])))

print(unique_counties)

with open("data/svi.csv", mode="w") as svi:
    svi.write("county, housing units, population, households, housing burden, disabled people, housing in structures with 10 or more units, mobile homes, housing units w more people than rooms, households wo vehicle, people in group quarters")
    for county in unique_counties:
        housing_units = data.loc[data['COUNTY'] == county, 'E_HU'].sum()
        population = data.loc[data['COUNTY'] == county, 'E_TOTPOP'].sum()
        households = data.loc[data['COUNTY'] == county, 'E_HH'].sum()
        hburd = data.loc[data['COUNTY'] == county,
                         'E_HBURD'].sum() / housing_units
        disabl = data.loc[data['COUNTY'] == county,
                          'E_DISABL'].sum() / population
        munit = data.loc[data['COUNTY'] == county,
                         'E_MUNIT'].sum() / housing_units
        mobile = data.loc[data['COUNTY'] == county,
                          'E_MOBILE'].sum() / housing_units
        crowd = data.loc[data['COUNTY'] == county,
                         'E_CROWD'].sum() / housing_units
        noveh = data.loc[data['COUNTY'] == county,
                         'E_NOVEH'].sum() / households
        groupq = data.loc[data['COUNTY'] == county,
                          'E_GROUPQ'].sum() / population
        svi.write("%s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n" % (county, housing_units,
                  population, households, hburd, disabl, munit, mobile, crowd, noveh, groupq))
