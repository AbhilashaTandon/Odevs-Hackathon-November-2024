from collections import Counter
from PIL import Image
from typing import Tuple
from osgeo import gdal
import matplotlib.pyplot as plt
from geography import FLORIDA_NORTH, FLORIDA_EAST, FLORIDA_SOUTH, FLORIDA_WEST
import numpy as np
from geography import get_tract
from svi import get_row


class GeoTiff:
    def __init__(self, path):
        self.data_obj = gdal.Open(path, gdal.GA_ReadOnly)
        self.transform = self.data_obj.GetGeoTransform()
        self.x_width = self.data_obj.RasterXSize
        self.y_width = self.data_obj.RasterYSize
        self.data = self.data_obj.GetRasterBand(1)

    def pixel_to_coord(self, x: int, y: int) -> Tuple[float, float]:
        """converts pixel on geotiff to latitude and longitude coordinates

        Args:
            x (int): pixel column
            y (int): pixel row

        Raises:
            ValueError: if pixel out of range

        Returns:
            Tuple[float, float]: longitude and latitude
        """
        if (x < 0 or x >= self.x_width):
            raise ValueError("Tried to lookup a pixel outside of range")
        elif (y < 0 or y >= self.y_width):
            raise ValueError("Tried to lookup a pixel outside of range")

        lon = self.transform[0] + x * self.transform[1] + y * self.transform[2]
        lat = self.transform[3] + x * self.transform[4] + y * self.transform[5]
        return lon, lat

    def coord_to_pixel(self, lon: float, lat: float) -> Tuple[int, int]:
        """converts latitude, longitude coordinates to pixel on geotiff

        Args:
            lon (float): longitude
            lat (float): latitude

        Returns:
            Tuple[int, int]: x and y pixel coordinates
        """

        det = 1. / \
            (self.transform[1] * self.transform[5] -
             self.transform[2] * self.transform[4])
        # multiply by inverse matrix
        centered_lon = lon - self.transform[0]
        centered_lat = lat - self.transform[3]
        x = centered_lon * self.transform[5] - centered_lat * self.transform[2]
        y = -centered_lon * self.transform[4] + \
            centered_lat * self.transform[1]
        return int(x*det + .5), int(y*det + .5)

    def get_value(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float, lon_entries: int, lat_entries: int):
        """Looks at rectangle of latitude/longitude and samples map with specified subdivisions

        Args:
            min_lon (float): minimum longitude, left side of rectangle
            min_lat (float): minimum latitude, top side of rectangle
            max_lon (float): maximum longitude, right side of rectangle
            max_lat (float): maximum latitude, bottom side of rectangle
            lon_entries (int): number of columns
            lat_entries (int): number of rows

        Returns:
            lat_entries x lon_entries np array: values of geotiff
        """
        left, top = self.coord_to_pixel(
            min_lon, min_lat)
        right, bottom = self.coord_to_pixel(
            max_lon, max_lat)
        x_size, y_size = right - left, bottom - top

        return self.data_obj.ReadAsArray(xoff=left, yoff=top, xsize=x_size, ysize=y_size, buf_xsize=lon_entries, buf_ysize=lat_entries, resample_alg=gdal.GRIORA_Bilinear)

# get maps for all severity risks
# cat 1 is a low risk scenario, cat 5 is a high risk


categories = [
    GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category1_MOM_Inundation_HIGH.tif"),
    GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category2_MOM_Inundation_HIGH.tif"),
    GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category3_MOM_Inundation_HIGH.tif"),
    GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category4_MOM_Inundation_HIGH.tif"),
    GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category5_MOM_Inundation_HIGH.tif")]


def get_severity(lon: float, lat: float, lon_sample_range: float, lat_sample_range: float) -> int:
    """Gets flood risk zone (0-5 inclusive: 0 no risk, 5 most risk) at lon, lat, averaged over lon_sample_range, lat_sample_range"""
    flood_risk_zone = 0

    for idx, category in enumerate(categories[::-1]):
        # iterate through them backwards because category 1 is most at risk, so we want to set it last so it isnt overwritten by broader maps
        map_data = category.get_value(lon - lon_sample_range/2, lat - lat_sample_range/2,
                                      lon + lon_sample_range/2, lat + lat_sample_range/2, 1, 1)
        # flood areas are non white pixels

        if (map_data < 255):
            flood_risk_zone = idx + 1

    return flood_risk_zone


def get_severity_range(min_lon: float, min_lat: float, max_lon: float, max_lat: float, lon_entries: int, lat_entries: int):
    """Gets flood risk zone (0-5 inclusive: 0 no risk, 5 most risk) in specified rectangle with specified subdivisions

    Args:
            min_lon (float): minimum longitude, left side of rectangle
            min_lat (float): minimum latitude, top side of rectangle
            max_lon (float): maximum longitude, right side of rectangle
            max_lat (float): maximum latitude, bottom side of rectangle
            lon_entries (int): number of columns
            lat_entries (int): number of rows
    """

    flood_risk_zone = np.zeros((lat_entries, lon_entries))

    for idx, category in enumerate(categories[::-1]):
        # iterate through them backwards because category 1 is most at risk, so we want to set it last so it isnt overwritten by broader maps
        map_data = category.get_value(min_lon, min_lat,
                                      max_lon, max_lat, lat_entries, lon_entries)
        # flood areas are non white pixels

        flood_risk_zone[map_data < 255] = idx + 1

    return flood_risk_zone


def gen_image():

    # get square bounding box of florida

    IMAGE_SIZE = 2000

    img = np.ones((IMAGE_SIZE, IMAGE_SIZE, 3)) * 255

    color_scale = [[29, 212, 108], [68, 236, 22], [
        224, 255, 32], [255, 144, 48], [255, 64, 64]]

    for idx, category in enumerate(categories[::-1]):
        # iterate through them backwards because category 1 is most at risk, so we want to set it last so it isnt overwritten by broader maps
        map_data = category.get_value(FLORIDA_WEST, FLORIDA_NORTH,
                                      FLORIDA_EAST, FLORIDA_SOUTH, IMAGE_SIZE, IMAGE_SIZE)
        # flood areas are non white pixels
        img[map_data < 255] = color_scale[idx]


def get_tract_stats():
    flood_zones_tracts = {}
    flood_zones_counties = {}

    import pandas as pd

    svi = pd.read_csv("raw/CDC SVI/Florida.csv")

    for _, row in svi.iterrows():
        flood_zones_tracts[row['FIPS']] = Counter()
        flood_zones_counties[row['STCNTY']] = Counter()

    IMAGE_SIZE = 20

    storm_risk_data = np.zeros((IMAGE_SIZE, IMAGE_SIZE))

    for idx, category in enumerate(categories[::-1]):
        # iterate through them backwards because category 1 is most at risk, so we want to set it last so it isnt overwritten by broader maps
        map_data = category.get_value(FLORIDA_WEST, FLORIDA_NORTH,
                                      FLORIDA_EAST, FLORIDA_SOUTH, IMAGE_SIZE, IMAGE_SIZE)
        storm_risk_data[map_data < 255] = idx + 1

    from alive_progress import alive_bar

    with alive_bar(IMAGE_SIZE * IMAGE_SIZE) as bar:
        for i in range(IMAGE_SIZE):
            for j in range(IMAGE_SIZE):
                bar()
                lon = FLORIDA_WEST + \
                    (FLORIDA_EAST - FLORIDA_WEST)/IMAGE_SIZE * i
                lat = FLORIDA_NORTH + \
                    (FLORIDA_SOUTH - FLORIDA_NORTH)/IMAGE_SIZE * j

                flood_zone = int(storm_risk_data[j][i])
                if (flood_zone > 0):
                    fips = get_tract(lon, lat)
                    county = fips // 1000000
                    if (fips > 1 and fips in flood_zones_tracts):
                        # print(lat, lon, flood_zone, fips)
                        flood_zones_tracts[fips][flood_zone] += 1
                        flood_zones_counties[county][flood_zone] += 1

    with open("tract_flood_risk.csv", mode='w') as output:
        output.write("fips, zone 1, zone 2, zone 3, zone 4, zone 5\n")
        for fips, value in flood_zones_tracts.items():
            if (value.total() > 0):
                output.write("%d, " % fips)
                for i in range(1, 6):
                    if (i not in set(value)):
                        num = 0
                    else:
                        num = value[i]

                    output.write("%d, " % num)
                try:
                    county_id = str(fips)[2:5]
                    tract_id = str(fips)[5:]
                    area = get_row(county_id, tract_id)["AREA_SQMI"]
                    print(county_id, tract_id)

                    output.write("%f, " % area)
                except Exception:
                    pass

                output.write("\n")


if __name__ == "__main__":
    get_tract_stats()
