import struct
from typing import Tuple
from osgeo import gdal
import matplotlib.pyplot as plt
from florida import FLORIDA_NORTH, FLORIDA_EAST, FLORIDA_SOUTH, FLORIDA_WEST


class GeoTiff:
    def __init__(self, path):
        self.data_obj = gdal.Open(path, gdal.GA_ReadOnly)
        self.transform = self.data_obj.GetGeoTransform()
        self.x_width = self.data_obj.RasterXSize
        self.y_width = self.data_obj.RasterYSize

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


def main():

    category_1 = GeoTiff(
        "raw/US_SLOSH_MOM_Inundation_v3/us_Category1_MOM_Inundation_HIGH.tif")

    min_x, min_y = category_1.coord_to_pixel(FLORIDA_WEST, FLORIDA_NORTH)
    max_x, max_y = category_1.coord_to_pixel(FLORIDA_EAST, FLORIDA_SOUTH)

    print(min_x, min_y, max_x, max_y)


if __name__ == "__main__":
    main()
