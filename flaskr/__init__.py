from flask import Flask
from flask import request
from flask_cors import CORS
import sys
import json
import re

from .rev_analysis import *
from .cohort_analysis import *
from .dashboard import *
from .cac import *

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return "Hello World!"

    @app.route('/analysis', methods=['POST'])
    def analysis():
        sheets = request.get_json()
        r = RevAnalysis(sheets["ARR by Customer"])
        r_res = r.run()
        c = CohortAnalysis(r_res["MRR by Customer"], r_res["Revenue Cohorts (Monthly)"])
        c_res = c.run()

        is_dict, bs_dict, cf_dict= {}, {}, {}
        for sheet_name in sheets.keys():
            match = re.search(r'(\d+)', sheet_name)
            if match:
                year = match.group()
                if "IS" in sheet_name:
                    is_dict[year] = sheets[sheet_name]
                if "BS" in sheet_name:
                    bs_dict[year] = sheets[sheet_name]
                if "CF" in sheet_name:
                    cf_dict[year] = sheets[sheet_name]

        d = Dashboard(r_res["MRR by Customer"], r_res["Revenue Cohorts (Monthly)"], is_dict, bs_dict, cf_dict)
        d_res = d.run()
        ca = CAC(d.fin_perf_raw, d_res["Operating Metrics"], d_res["Other Metrics"])
        ca_res = ca.run()
        return json.dumps({**r_res, **c_res, **d_res, **ca_res})

    return app
