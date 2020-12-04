'''Python script to generate Revenue Analysis given ARR by Customer'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
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

        self.clean_outputs()
        json = {
            "MRR by Customer": self.mrr.to_dict(orient='records'),
            "Revenue Cohorts": self.rev_cohorts.to_dict(orient='records')
        }
        return json

    def clean_inputs(self):
        self.arr.set_index("Customer", inplace=True)
        self.arr.apply(dollars_to_dec)
        # print(self.arr_by_customer, file=sys.stdout)

    def clean_outputs(self):
        self.mrr.apply(dec_to_dollars)
        self.mrr.reset_index(inplace=True)
        self.rev_cohorts.iloc[:, 1:] = self.rev_cohorts.iloc[:, 1:].apply(dec_to_dollars)
        self.rev_cohorts.reset_index(inplace=True)

        print("MRR BY CUSTOMER")
        print(self.mrr, file=sys.stdout)
        print("REVENUE COHORTS")
        print(self.rev_cohorts, file=sys.stdout)

    def mrr_by_customer(self):
        # 1. MRR BY CUSTOMER
        self.mrr = self.arr.copy()/12
        self.mrr.loc["ARR"] = (self.mrr.iloc[-1:]*12).iloc[0]

    def rev_cohorts(self):
        # 1. REV COHORTS
        first_rev = np.argmax(self.mrr.values!=0.0,axis=1)
        last_rev = self.mrr.shape[1] - np.argmax(self.mrr.iloc[:, ::-1].values!=0.0,axis=1) - 1
        print(np.argmax(self.mrr.iloc[:, ::-1].values!=0.0,axis=1))
        print(last_rev)

        self.rev_cohorts = pd.DataFrame(index=np.arange(self.mrr.shape[0]))
        self.rev_cohorts.set_index(self.mrr.index, inplace=True)
        self.rev_cohorts['Cohort'] = self.mrr.keys()[first_rev]
        self.rev_cohorts['Cohort'] = pd.to_datetime(self.rev_cohorts['Cohort']).dt.strftime('%m/%Y')

        initial_rev_column, end_rev_column = [], []
        for i in range(len(first_rev)):
            initial_rev_column.append(self.mrr.iloc[i][first_rev[i]])
            end_rev_column.append(self.mrr.iloc[i][last_rev[i]])
        self.rev_cohorts['Initial Rev'] = initial_rev_column
        self.rev_cohorts['End Rev'] = end_rev_column
        self.rev_cohorts['Initial Rev'] = self.rev_cohorts['Initial Rev'].astype(object)
        self.rev_cohorts['End Rev'] = self.rev_cohorts['End Rev'].astype(object)
        self.rev_cohorts.drop(self.rev_cohorts.tail(2).index, inplace=True)

    def rev_analysis(self):
        # 1. REV ANALYSIS
        print("REVENUE ANALYSIS")
        rev_analysis_final = self.data/12

        print(rev_analysis_final, file=sys.stdout)
        return rev_analysis_final.to_json(orient='records')
