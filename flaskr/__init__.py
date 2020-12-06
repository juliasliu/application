from flask import Flask
from flask import request
from flask_cors import CORS
import sys
import json

from .rev_analysis import *
from .cohort_analysis import *
from .dashboard import *

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
        r = RevAnalysis(request.get_json()["ARR by Customer"])
        r_res = r.run()
        c = CohortAnalysis(r_res["MRR by Customer"], r_res["Revenue Cohorts (Monthly)"])
        c_res = c.run()
        d = Dashboard(r_res["MRR by Customer"], r_res["Revenue Cohorts (Monthly)"])
        d_res = d.run()
        return json.dumps({**r_res, **c_res, **d_res})

    return app
