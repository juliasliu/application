'''Python script to generate Revenue Analysis given ARR by Customer'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections
import sys

from .helpers import *

class RevAnalysis:

    def __init__(self, json):
        print("INIT REV ANALYSIS", file=sys.stdout)
        self.arr = pd.DataFrame(json)

    def run(self):
        self.clean_inputs()
        print(self.arr, file=sys.stdout)

        self.mrr_by_customer()
        self.rev_cohorts()
        self.cy_ttm_revenue()

        self.clean_outputs()
        json = {
            "MRR by Customer": self.mrr.to_dict(orient='records'),
            "Revenue Cohorts": self.rev_cohorts.to_dict(orient='records'),
            "CY TTM Revenue": self.cy_ttm_revenue.to_dict(orient='records')
        }
        return json

    def clean_inputs(self):
        self.arr.set_index("Customer", inplace=True)
        self.arr.apply(dollars_to_dec)

    def clean_outputs(self):
        self.mrr.apply(dec_to_dollars)
        self.mrr.reset_index(inplace=True)

        self.rev_cohorts.iloc[:, 1:] = self.rev_cohorts.iloc[:, 1:].astype(object)
        self.rev_cohorts.iloc[:, 1:] = self.rev_cohorts.iloc[:, 1:].apply(dec_to_dollars)
        self.rev_cohorts.reset_index(inplace=True)

        self.cy_ttm_revenue = self.cy_ttm_revenue.astype(object)
        self.cy_ttm_revenue.apply(dec_to_dollars)
        self.cy_ttm_revenue.reset_index(inplace=True)

        print("MRR BY CUSTOMER")
        print(self.mrr, file=sys.stdout)
        print("REVENUE COHORTS")
        print(self.rev_cohorts, file=sys.stdout)
        print("CY TTM REVENUE")
        print(self.cy_ttm_revenue, file=sys.stdout)

    def mrr_by_customer(self):
        # 1. MRR BY CUSTOMER
        self.mrr = self.arr.copy()/12
        self.mrr.loc["ARR"] = (self.mrr.iloc[-1:]*12).iloc[0]

    def rev_cohorts(self):
        # 1. REV COHORTS
        first_rev = np.argmax(self.mrr.values!=0.0,axis=1)
        last_rev = self.mrr.shape[1] - np.argmax(self.mrr.iloc[:, ::-1].values!=0.0,axis=1) - 1

        self.rev_cohorts = pd.DataFrame(index=np.arange(self.mrr.shape[0]))
        self.rev_cohorts.set_index(self.mrr.index, inplace=True)
        self.rev_cohorts['Cohort'] = self.mrr.keys()[first_rev]
        self.rev_cohorts['Cohort'] = pd.to_datetime(self.rev_cohorts['Cohort']).dt.strftime('%m/%Y')
        self.rev_cohorts['Initial Rev'] = [self.mrr.iloc[i][first_rev[i]] for i in range(len(first_rev))]
        self.rev_cohorts['End Rev'] = [self.mrr.iloc[i][last_rev[i]] for i in range(len(last_rev))]

        self.rev_cohorts.drop(self.rev_cohorts.tail(2).index, inplace=True)

    def cy_ttm_revenue(self):
        # 1. CY, TTM, ARR
        self.cy_ttm_revenue = pd.DataFrame(index=np.arange(self.mrr.shape[0]))
        self.cy_ttm_revenue.set_index(self.mrr.index, inplace=True)

        years = pd.to_datetime(self.mrr.keys()).strftime('%Y')
        counter = collections.Counter(years)
        for year in counter.keys():
            if counter[year] == 12:
                # Calculate CY for each full year
                current_year_indices = [i for i in range(len(years)) if years[i] == year]
                current_year_columns = self.mrr.iloc[:,current_year_indices]
                self.cy_ttm_revenue["CY "+year] = current_year_columns.sum(axis=1)
                # Calculate ARRs for the last month of each full year
                self.cy_ttm_revenue["12/"+year+" ARR"] = current_year_columns.iloc[:, -1:]*12

        # Calculate TTM for the last month
        mrr_ttm = self.mrr.iloc[:, -12:]
        self.cy_ttm_revenue["TTM "+mrr_ttm.columns[-1]] = mrr_ttm.sum(axis=1)
        # Calculate ARR for the last month
        self.cy_ttm_revenue[mrr_ttm.columns[-1]+" ARR"] = mrr_ttm.iloc[:, -1:]*12

        # Calculate CY YoY for each pair of CYs
        cy_labels = [label for label in self.cy_ttm_revenue.keys() if "CY" in label]
        cy_columns = self.cy_ttm_revenue.loc[:,cy_labels]
        for i in range(1, cy_columns.shape[1]):
            prev_cy = pd.Series(cy_columns.iloc[:, i-1])
            curr_cy = pd.Series(cy_columns.iloc[:, i])
            yoy = [((curr_cy[j]/prev_cy[j]-1)*100 if prev_cy[j] != 0 else 0) for j in range(len(prev_cy))]
            self.cy_ttm_revenue[cy_columns.keys()[i]+" YOY"] = yoy

        columns_sorted = sorted(self.cy_ttm_revenue.columns)
        cy = [col for col in columns_sorted if "CY" in col and "YOY" not in col]
        ttm = [col for col in columns_sorted if "TTM" in col]
        yoy = [col for col in columns_sorted if "YOY" in col]
        arr = [col for col in columns_sorted if "ARR" in col]
        self.cy_ttm_revenue = self.cy_ttm_revenue.reindex(cy + ttm + yoy + arr, axis=1)
        self.cy_ttm_revenue.drop(self.cy_ttm_revenue.tail(2).index, inplace=True)

    def rev_analysis(self):
        # 1. REV ANALYSIS
        print("REVENUE ANALYSIS")
        rev_analysis_final = self.data/12

        print(rev_analysis_final, file=sys.stdout)
        return rev_analysis_final.to_json(orient='records')
