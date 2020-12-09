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
from .payback_chart import *
from .rev_charts import *
from .benchmark import *

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

    def analysis_helper(companies):
        company_dict = {}
        for company in companies.keys():
            sheets = companies[company]

            r = RevAnalysis(sheets["ARR by Customer"])
            r_res = r.run()
            c = CohortAnalysis(r.mrr, r.rev_cohorts)
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
            years = sorted(is_dict.keys())
            start_year = years[0]
            end_year = years[-1]

            d = Dashboard(r.mrr, r.rev_cohorts, is_dict, bs_dict, cf_dict)
            d_res = d.run()
            ca = CAC(d.fin_perf_raw, d.oper_metrics, d.oth_metrics)
            ca_res = ca.run()
            p = PaybackChart(c.rev_cohorts, c.cumulative, d.oper_stats_raw, ca.cac_ttm)
            p_res = p.run()
            rev = RevCharts(d.rev_build)
            rev_res = rev.run()

            company_dict[company] = {
                "Rev Analysis": r_res,
                "Cohort Analysis": c_res,
                "Dashboard": d_res,
                "CAC": ca_res,
                "Payback Chart": p_res,
                "Rev Charts": rev_res,
                "start_year": start_year,
                "end_year": end_year,
            }

        return company_dict

    # a simple page that says hello
    @app.route('/')
    def hello():
        return "Hello World!"

    @app.route('/analysis', methods=['POST'])
    def analysis():
        companies = request.get_json()
        return json.dumps(analysis_helper(companies))

    @app.route('/benchmark', methods=['POST'])
    def benchmark():
        companies = request.get_json()

        # Run analysis on individual companies
        company_dict = analysis_helper(companies)
        b = Benchmark(company_dict)
        b_res = b.run()
        res = {
            "Benchmark": { "Benchmark": b_res },
            **company_dict,
        }
        return json.dumps(res)

    return app
