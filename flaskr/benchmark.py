'''Python script to benchmark different companies'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class Benchmark:

    # ARR
    # ARR YoY growth
    # Total Revenue
    # Total Revenue YoY growth
    # Gross margin
    # Contribution margin
    # EBITDA Margin
    # Last Month Cash Burn (CFO - CFI)
    # S&M as % of Rev
    # R&D as % of Rev
    # G&A as % of Rev
    # M13 Net $ Retention
    # M13 Gross Logo Retention
    # M13 Avg Cumulative Revenue Per Customer
    # CAC (last quarter)
    # Number of Customers (last month)
    # Avg ARR per Customer
    # Net New ARR in last Quarter
    # Net New ARR in last Quarter / Cash Burn in Last Quarter

    def __init__(self, companies):
        print("INIT BENCHMARK")
        self.fin_perf, self.oper_stats, self.cash_flow_stat, self.oth_metrics, self.rev_retention, self.logo_retention, self.cumulative, self.cac = {}, {}, {}, {}, {}, {}, {}, {}
        for company in companies.keys():
            self.fin_perf[company] = pd.DataFrame(companies[company]["Dashboard"]["Financial Performance"])
            self.oper_stats[company] = pd.DataFrame(companies[company]["Dashboard"]["Operating Statistics"])
            self.cash_flow_stat[company] = pd.DataFrame(companies[company]["Dashboard"]["Cash Flow Statement"])
            self.oth_metrics[company] = pd.DataFrame(companies[company]["Dashboard"]["Other Metrics"])
            self.rev_retention[company] = pd.DataFrame(companies[company]["Cohort Analysis"]["Revenue Retention (Monthly)"])
            self.logo_retention[company] = pd.DataFrame(companies[company]["Cohort Analysis"]["Logo Retention (Monthly)"])
            self.cumulative[company] = pd.DataFrame(companies[company]["Cohort Analysis"]["Cumulative Revenue Per Customer (Monthly)"])
            self.cac[company] = pd.DataFrame(companies[company]["CAC"]["CAC & CAC TTM"])

    def run(self):
        self.clean_inputs()
        print(self.fin_perf)
        print(self.oper_stats)
        print(self.cash_flow_stat)
        print(self.oth_metrics)
        print(self.rev_retention)
        print(self.logo_retention)
        print(self.cumulative)
        print(self.cac)

        self.benchmark()

        self.clean_outputs()
        json = {
            "Benchmark": self.bm.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        for company in self.fin_perf.keys():
            self.fin_perf[company] = self.fin_perf[company].copy()
            self.fin_perf[company].set_index("Financial Performance", inplace=True)
            self.fin_perf[company].apply(filter_to_dec_list)
            self.oper_stats[company] = self.oper_stats[company].copy()
            self.oper_stats[company].set_index("Operating Statistics", inplace=True)
            self.oper_stats[company].apply(filter_to_dec_list)
            self.cash_flow_stat[company] = self.cash_flow_stat[company].copy()
            self.cash_flow_stat[company].set_index("Cash Flow Statement", inplace=True)
            self.cash_flow_stat[company].apply(filter_to_dec_list)
            self.oth_metrics[company] = self.oth_metrics[company].copy()
            self.oth_metrics[company].set_index("Other Metrics", inplace=True)
            self.oth_metrics[company].apply(filter_to_dec_list)
            self.rev_retention[company] = self.rev_retention[company].copy()
            self.rev_retention[company].set_index("Cohort", inplace=True)
            self.rev_retention[company].apply(filter_to_dec_list)
            self.logo_retention[company] = self.logo_retention[company].copy()
            self.logo_retention[company].set_index("Cohort", inplace=True)
            self.logo_retention[company].apply(filter_to_dec_list)
            self.cumulative[company] = self.cumulative[company].copy()
            self.cumulative[company].set_index("Cohort", inplace=True)
            self.cumulative[company].apply(filter_to_dec_list)
            self.cac[company] = self.cac[company].copy()
            self.cac[company].set_index(self.cac[company].columns[0], inplace=True)
            self.cac[company].apply(filter_to_dec_list)

    def clean_outputs(self):
        self.bm = self.bm.astype(object)
        self.bm.apply(nan_to_blank_list)
        base_build_copy = self.bm.copy()
        self.bm = self.bm.apply(numbers_with_commas_list)
        # self.bm.loc['Churn %'] = base_build_copy.loc['Churn %'].apply(dec_to_percents)
        self.bm.reset_index(inplace=True)

        print("Benchmark")
        print(self.bm)

    def benchmark(self):
        self.bm = self.fin_perf["Icertis"].copy()
