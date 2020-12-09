'''Python script to benchmark different companies'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class Benchmark:

    def __init__(self, companies):
        print("INIT BENCHMARK")
        self.mrr, self.fin_perf, self.oper_stats, self.cash_flow_stat, self.oth_metrics, self.rev_retention, self.logo_retention, self.cumulative = {}, {}, {}, {}, {}, {}, {}, {}
        self.companies = companies;
        for company in companies.keys():
            self.mrr[company] = pd.DataFrame(companies[company]["Rev Analysis"]["MRR by Customer"])
            self.fin_perf[company] = pd.DataFrame(companies[company]["Dashboard"]["Financial Performance"])
            self.oper_stats[company] = pd.DataFrame(companies[company]["Dashboard"]["Operating Statistics"])
            self.cash_flow_stat[company] = pd.DataFrame(companies[company]["Dashboard"]["Cash Flow Statement"])
            self.oth_metrics[company] = pd.DataFrame(companies[company]["Dashboard"]["Other Metrics"])
            self.rev_retention[company] = pd.DataFrame(companies[company]["Cohort Analysis"]["Revenue Retention (Monthly)"])
            self.logo_retention[company] = pd.DataFrame(companies[company]["Cohort Analysis"]["Logo Retention (Monthly)"])
            self.cumulative[company] = pd.DataFrame(companies[company]["Cohort Analysis"]["Cumulative Revenue Per Customer (Monthly)"])

    def run(self):
        self.clean_inputs()
        print(self.mrr)
        print(self.fin_perf)
        print(self.oper_stats)
        print(self.cash_flow_stat)
        print(self.oth_metrics)
        print(self.rev_retention)
        print(self.logo_retention)
        print(self.cumulative)

        self.benchmark()

        self.clean_outputs()
        json = {
            "Benchmark": self.bm.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        for company in self.companies.keys():
            self.mrr[company] = self.mrr[company].copy()
            self.mrr[company].set_index("Customer", inplace=True)
            self.mrr[company].apply(filter_to_dec_list)
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

    def clean_outputs(self):
        self.bm = self.bm.astype(object)
        self.bm.apply(nan_to_blank_list)
        bm_copy = self.bm.copy()
        self.bm = self.bm.apply(numbers_with_commas_list)
        self.bm['ARR YoY Growth'] = bm_copy['ARR YoY Growth'].apply(dec_to_percents)
        self.bm['Total Revenue YoY Growth'] = bm_copy['Total Revenue YoY Growth'].apply(dec_to_percents)
        self.bm['Gross Margin'] = bm_copy['Gross Margin'].apply(dec_to_percents)
        self.bm['Contribution Margin'] = bm_copy['Contribution Margin'].apply(dec_to_percents)
        self.bm['EBITDA Margin'] = bm_copy['EBITDA Margin'].apply(dec_to_percents)
        self.bm['M13 Net Rev Retention'] = bm_copy['M13 Net Rev Retention'].apply(dec_to_percents)
        self.bm['M13 Gross Logo Retention'] = bm_copy['M13 Gross Logo Retention'].apply(dec_to_percents)
        self.bm['S&M as % of Rev'] = bm_copy['S&M as % of Rev'].apply(dec_to_percents)
        self.bm['R&D as % of Rev'] = bm_copy['R&D as % of Rev'].apply(dec_to_percents)
        self.bm['G&A as % of Rev'] = bm_copy['G&A as % of Rev'].apply(dec_to_percents)
        self.bm.reset_index(inplace=True)

        print("Benchmark")
        print(self.bm)

    def label_helper(self, row_label):
        sheet_source = self.bm_dict[row_label][0]
        old_label = self.bm_dict[row_label][1]
        col_label = self.bm_dict[row_label][2]
        values = [(sheet_source[company].loc[old_label, col_label] if old_label in sheet_source[company].index and col_label in sheet_source[company].columns else float("NaN")) for company in self.companies.keys()]
        self.bm[row_label] = values

    def benchmark(self):
        self.bm_dict = {
            "ARR": [self.fin_perf, "ARR", list(self.fin_perf.values())[0].columns[-1]],
            "ARR YoY Growth": [self.oper_stats, "ARR YoY", list(self.fin_perf.values())[0].columns[-1]],
            "Total Revenue": [self.fin_perf, "Revenue", list(self.fin_perf.values())[0].columns[-1]],
            "Total Revenue YoY Growth": [self.oper_stats, "Revenue YoY", list(self.fin_perf.values())[0].columns[-1]],
            "Gross Margin": [self.oper_stats, "Gross Margin", list(self.oper_stats.values())[0].columns[-1]],
            "Contribution Margin": [self.oper_stats, "Contribution Margin", list(self.oper_stats.values())[0].columns[-1]],
            "EBITDA Margin": [self.oper_stats, "EBITDA Margin", list(self.oper_stats.values())[0].columns[-1]],
            "Avg ARR per Customer": [self.oth_metrics, "Avg ARR per Customer", list(self.oth_metrics.values())[0].columns[-1]],
            "M13 Net Rev Retention": [self.rev_retention, "Median", "M13"],
            "M13 Gross Logo Retention": [self.logo_retention, "Median", "M13"],
            "M13 Avg Cumulative Revenue Per Customer": [self.cumulative, "Median", "M13"]
        }
        self.bm = pd.DataFrame(index=np.arange(len(self.companies)), columns=self.bm_dict.keys())
        self.bm.set_index(pd.Series(self.companies.keys(), name='Company'), inplace=True)

        for label in self.bm_dict.keys():
            self.label_helper(label)

        self.bm["Number of Customers in Last Month"] = [self.mrr[company].iloc[:, -1].count() for company in self.companies.keys()]
        self.bm["Last Month Cash Burn (CFO - CFI)"] = [self.cash_flow_stat[company].loc["CFO"].iloc[-1]-self.cash_flow_stat[company].loc["CFI"].iloc[-1] for company in self.companies.keys()]
        self.bm["S&M as % of Rev"] = [self.fin_perf[company].loc["S&M"].iloc[-1]/self.fin_perf[company].loc["Revenue"].iloc[-1] for company in self.companies.keys()]
        self.bm["R&D as % of Rev"] = [self.fin_perf[company].loc["R&D"].iloc[-1]/self.fin_perf[company].loc["Revenue"].iloc[-1] for company in self.companies.keys()]
        self.bm["G&A as % of Rev"] = [self.fin_perf[company].loc["G&A"].iloc[-1]/self.fin_perf[company].loc["Revenue"].iloc[-1] for company in self.companies.keys()]

        bm_copy = self.bm.astype('float64')
        self.bm.loc["Min"] = self.bm[self.bm != "NaN"].min()
        self.bm.loc["25th Percentile"] = self.bm[self.bm != "NaN"].quantile(0.25)
        self.bm.loc["Median"] = self.bm[self.bm != "NaN"].median()
        self.bm.loc["Mean"] = self.bm[self.bm != "NaN"].mean()
        self.bm.loc["75th Percentile"] = self.bm[self.bm != "NaN"].quantile(0.75)
        self.bm.loc["Max"] = self.bm[self.bm != "NaN"].max()
