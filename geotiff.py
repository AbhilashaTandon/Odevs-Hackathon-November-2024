from PIL import Image
import struct
from typing import Tuple
from osgeo import gdal
import matplotlib.pyplot as plt
from florida import FLORIDA_NORTH, FLORIDA_EAST, FLORIDA_SOUTH, FLORIDA_WEST
import numpy as np


class GeoTiff:
    def __init__(self, path):
        self.data_obj = gdal.Open(path, gdal.GA_ReadOnly)
        self.transform = self.data_obj.GetGeoTransform()
        self.x_width = self.data_obj.RasterXSize
        self.y_width = self.data_obj.RasterYSize
        print(self.x_width, self.y_width)
        self.data = self.data_obj.GetRasterBand(1)

    def pixel_to_coord(self, x: int, y: int) -> Tuple[float, float]:
        if (x < 0 or x >= self.x_width):
            raise ValueError("Tried to lookup a pixel outside of range")

        lon = self.transform[0] + x * self.transform[1] + y * self.transform[2]
        lat = self.transform[3] + x * self.transform[4] + y * self.transform[5]
        return lon, lat

    def coord_to_pixel(self, lon: float, lat: float) -> Tuple[int, int]:
        # multiply by inverse matrix
        det = 1. / \
            (self.transform[1] * self.transform[5] -
             self.transform[2] * self.transform[4])
        centered_lon = lon - self.transform[0]
        centered_lat = lat - self.transform[3]
        x = centered_lon * self.transform[5] - centered_lat * self.transform[2]
        y = -centered_lon * self.transform[4] + \
            centered_lat * self.transform[1]
        return int(x*det + .5), int(y*det + .5)

    def get_value(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float, lon_entries: int, lat_entries: int):
        left, top = self.coord_to_pixel(
            min_lon, min_lat)
        right, bottom = self.coord_to_pixel(
            max_lon, max_lat)
        x_size, y_size = right - left, bottom - top

        return self.data_obj.ReadAsArray(xoff=left, yoff=top, xsize=x_size, ysize=y_size, buf_xsize=lon_entries, buf_ysize=lat_entries, resample_alg=gdal.GRIORA_Bilinear)


def main():

    # get maps for all severity risks
    # cat 1 is a low risk scenario, cat 5 is a high risk

    categories = [
        GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category1_MOM_Inundation_HIGH.tif"),
        GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category2_MOM_Inundation_HIGH.tif"),
        GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category3_MOM_Inundation_HIGH.tif"),
        GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category4_MOM_Inundation_HIGH.tif"),
        GeoTiff("raw/US_SLOSH_MOM_Inundation_v3/us_Category5_MOM_Inundation_HIGH.tif")]

    # get square bounding box of florida

    IMAGE_SIZE = 1000

    img = np.ones((1000, 1000, 3)) * 255

    color_scale = [[67, 255, 40], [221, 243, 21], [
        231, 120, 4], [219, 0, 61], [207, 0, 207]]

    for idx, category in enumerate(categories[::-1]):
        # iterate through them backwards because category 1 is most at risk, so we want to set it last so it isnt overwritten by broader maps
        map_data = category.get_value(FLORIDA_WEST, FLORIDA_NORTH,
                                      FLORIDA_EAST, FLORIDA_SOUTH, 1000, 1000)
        # flood areas are non white pixels
        img[map_data < 255] = color_scale[idx]

    Image.fromarray(img.astype(np.uint8)).show()


if __name__ == "__main__":
    main()
