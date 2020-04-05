from flask import Flask, abort
from flask import render_template
import json
import os
import logging
from flask import render_template, flash, redirect, session, url_for, request, g
from werkzeug.exceptions import BadRequestKeyError

from covid19ca import ca_data_parser

app = Flask(__name__)

STATIC_FOLDER = os.path.join('static')
#full_filename = os.path.join(STATIC_FOLDER, 'log_graph_CA.png')

state_county_dict = {}
with open(os.path.join(STATIC_FOLDER, 'county_state_mapping')) as f:
    state_county_dict= json.load(f)

print(state_county_dict)


@app.route('/get_graph', methods=['GET','POST'])
def handle_graph():
    logger = app.logger
    logger.debug("form: %s", request.form)
    try:
        graph = request.form['graph']
    except BadRequestKeyError:
        logger.warning("no graph parameter!")
        abort(400)

    logger.debug("graph parameter: [%s]", graph)
    splits = graph.split(":")
    if len(splits) != 2:
        logger.warning("invalid graph parameter!")
        abort(400)

    state, county = splits[:2]
    counties = { county: state}
    county_info = ca_data_parser.get_county_data_from_csv(counties)
    date_range = ca_data_parser.get_date_range(county_info)
    ca_data_parser.create_count_csv(counties.keys(), county_info, date_range)

    filename = state + county + ".png"
    full_filename = os.path.join(STATIC_FOLDER, filename)
    ca_data_parser.plot_counties(counties, full_filename)
    return render_template('graph.html', covid_graph=full_filename, county_states=state_county_dict)


@app.route('/')
def index():
    return render_template('index.html',  county_states=state_county_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)