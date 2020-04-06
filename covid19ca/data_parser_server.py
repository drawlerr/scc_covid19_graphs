import urllib

import werkzeug
from flask import Flask, abort
import json
import os
from flask import render_template, request
from werkzeug.exceptions import BadRequestKeyError

from covid19ca import ca_data_parser

app = Flask(__name__)

STATIC_FOLDER = os.path.join('static')

with open(os.path.join(STATIC_FOLDER, 'county_state_mapping')) as f:
    state_county_dict = json.load(f)


@app.route('/graph/<url_state>/<url_county>', methods=['GET', 'POST'])
def handle_graph(url_state, url_county):
    logger = app.logger
    state = url_state.replace("_", " ")
    county = url_county.replace("_", " ")

    logger.debug("%s,%s: %s,%s", url_state, url_county, state, county)
    counties = {county: state}
    county_info = ca_data_parser.get_county_data_from_csv(counties)
    date_range = ca_data_parser.get_date_range(county_info)
    ca_data_parser.create_count_csv(counties.keys(), county_info, date_range)

    filename = f"{url_state}/{url_county}.png"
    full_filename = os.path.join(STATIC_FOLDER, filename)
    # if not os.path.exists(full_filename):
    statedir = os.path.join(STATIC_FOLDER,state)
    if not os.path.exists(statedir):
        os.mkdir(statedir)
    ca_data_parser.plot_counties(counties, full_filename)
    logger.debug("rendered chart to %s", full_filename)
    return render_template('index.html', covid_graph=filename,
                           county_states=state_county_dict)


@app.route('/')
def index():
    return render_template('index.html', county_states=state_county_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
