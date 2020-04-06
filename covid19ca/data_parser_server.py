import json
import os
import uuid

from flask import Flask, jsonify, url_for
from flask import render_template, request
from flask.json import loads

from covid19ca import ca_data_parser

app = Flask(__name__)

STATIC_FOLDER = os.path.join('static')

with open(os.path.join(STATIC_FOLDER, 'county_state_mapping')) as f:
    state_county_dict = json.load(f)


def render_graph(counties):
    logger = app.logger
    county_info = ca_data_parser.get_county_data_from_csv(counties)

    date_range = ca_data_parser.get_date_range(county_info)
    ca_data_parser.create_count_csv(counties, county_info, date_range)

    filename = f"{uuid.uuid4()}.png"
    full_filename = os.path.join(STATIC_FOLDER, filename)
    ca_data_parser.plot_counties(counties, full_filename)
    logger.debug("rendered chart to %s", full_filename)
    return filename


@app.route('/graph', methods=['GET', 'POST'])
def handle_graph():
    logger = app.logger

    counties = [loads(o) for o in request.json]
    logger.debug(counties)

    filename = render_graph(counties=counties)

    return jsonify({
        "covid_graph": url_for("static", filename=filename)
    })


@app.route('/')
def index():
    return render_template('index.html', county_states=state_county_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
