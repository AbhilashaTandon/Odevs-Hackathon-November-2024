from flask import Flask

app = Flask(__name__)


@app.route("/flood_zone")
def get_flood_zone():
    return {}
