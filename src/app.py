from flask import Flask
from data_api.slosh_mom import get_severity_range

app = Flask(__name__)


@app.route("/flood_zone?north=<float:north>?south=<float:south>?east=<float:east>?west=<float:west>?height=<int:height>?width=<int:width>")
def get_flood_zone(north: float, south: float, east: float, west: float, height: int, width: int):
    return {
        "zones": get_severity_range(west, north, east, south, width, height)
    }
