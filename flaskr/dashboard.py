'''Python script to generate Dashboard'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class Dashboard:

    def __init__(self, mrr, cohorts):
        print("INIT DASHBOARD")
        self.mrr = pd.DataFrame(mrr)
        self.cohorts = pd.DataFrame(cohorts)

    def run(self):
        self.clean_inputs()
        print(self.mrr)
        print(self.cohorts)

        self.base_build_support()
        self.rev_build_support()

        self.clean_outputs()
        json = {
            "BASE Build Support": self.base_build.to_dict(orient='records'),
            "Rev Build Support": self.rev_build.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        self.mrr.set_index("Customer", inplace=True)
        self.mrr.apply(dollars_to_dec_list)
        self.mrr.drop(self.mrr.tail(1).index, inplace=True)
        self.cohorts.set_index("Customer", inplace=True)
        self.cohorts.iloc[:, 1:-1] = self.cohorts.iloc[:, 1:-1].apply(dollars_to_dec_list)
        self.cohorts = self.cohorts[self.cohorts['Cohort']!="N/A"]

    def clean_outputs(self):
        self.base_build = self.base_build.astype(object)
        self.base_build.apply(na_to_blank_list)
        base_build_copy = self.base_build.copy()
        self.base_build = base_build_copy.apply(numbers_with_commas_list)
        self.base_build.loc['Churn %'] = base_build_copy.loc['Churn %'].apply(dec_to_percents)
        self.base_build.reset_index(inplace=True)

        self.rev_build = self.rev_build.astype(object)
        self.rev_build.apply(na_to_blank_list)
        rev_build_copy = self.rev_build.copy()
        self.rev_build = rev_build_copy.apply(numbers_with_commas_list)
        self.rev_build.loc['Churn %'] = rev_build_copy.loc['Churn %'].apply(dec_to_percents)
        self.rev_build.loc['Upsell %'] = rev_build_copy.loc['Upsell %'].apply(dec_to_percents)
        self.rev_build.loc['New customer %'] = rev_build_copy.loc['New customer %'].apply(dec_to_percents)
        self.rev_build.reset_index(inplace=True)

        print("BASE Build Support")
        print(self.base_build)
        print("Rev Build Support")
        print(self.rev_build)

    def base_build_support(self):
        # Create intermediate table for calculating BASE
        self.base_interm = self.mrr.iloc[:-1].copy()
        self.base_interm.columns = pd.to_datetime(self.base_interm.columns).strftime('%m/%Y')
        for c in self.base_interm.index:
            if c in self.cohorts.index:
                cust_cohort = str_to_datetime(self.cohorts.loc[c, "Cohort"])
                cust_end = str_to_datetime(self.cohorts.loc[c, "End"])
                self.base_interm.loc[c] = [str_to_datetime(month) >= cust_cohort and str_to_datetime(month) <= cust_end for month in self.base_interm.columns]
            else:
                self.base_interm.loc[c] = [False]*self.base_interm.shape[1]

        # Calculate BASE table
        base_index = ["B", "A", "S", "E", "Churn %"]
        self.base_build = pd.DataFrame(index=np.arange(len(base_index)), columns=self.base_interm.columns)
        self.base_build.set_index(pd.Series(base_index, name='Total Customers'), inplace=True)
        self.base_build.loc['E'] = self.base_interm.sum()
        self.base_build.loc['B'] = ["NaN"] + list(self.base_build.loc['E'].iloc[:-1])
        a = []
        for i in range(1, self.base_build.shape[1]):
            a.append(len(self.base_interm[(self.base_interm.iloc[:, i-1] == 0) & (self.base_interm.iloc[:, i] == 1)]))
        self.base_build.loc['A'] = ["NaN"] + a
        self.base_build.loc['S'] = ["NaN"] + list(self.base_build.loc['E'].iloc[1:]-self.base_build.loc['B'].iloc[1:]-self.base_build.loc['A'].iloc[1:])
        self.base_build.loc['Churn %'] = ["NaN"] + list(self.base_build.loc['S'].iloc[1:]/self.base_build.loc['B'].iloc[1:])

    def rev_build_support(self):
        # Calculate upsell formulas
        self.upsell = self.mrr.iloc[:-1].copy()
        self.upsell.columns = pd.to_datetime(self.upsell.columns).strftime('%m/%Y')
        self.upsell = self.upsell.apply(lambda x: pd.Series([0]+[max(0, min(x[i]-x[i-1], x[i], x[i-1])) for i in range(1, x.shape[0])], self.upsell.columns), axis=1)

        # Calculate decrease MRR formulas
        self.decrease_mrr = self.mrr.iloc[:-1].copy()
        self.decrease_mrr.columns = pd.to_datetime(self.decrease_mrr.columns).strftime('%m/%Y')
        self.decrease_mrr = self.decrease_mrr.apply(lambda x: pd.Series([0]+[max(float('-inf'), min(x[i]-x[i-1], x[i], x[i-1], 0)) for i in range(1, x.shape[0])], self.decrease_mrr.columns), axis=1)

        # Calculate final Total MRR table
        total_mrr_index = ["Beginning balance", "Lost customers", "Decrease", "Increase", "New customers", "Ending", "Total Additions", "Total Subtractions", "Churn %", "Upsell %", "New customer %"]
        self.rev_build = pd.DataFrame(index=np.arange(len(total_mrr_index)), columns=self.upsell.columns)
        self.rev_build.set_index(pd.Series(total_mrr_index, name='Total MRR'), inplace=True)
        self.rev_build.loc['Ending'] = list(self.mrr.loc['Grand Total'])
        self.rev_build.loc['Beginning balance'] = ["NaN"] + list(self.rev_build.loc['Ending'].iloc[:-1])
        l, n = [], []
        for i in range(1, self.mrr.shape[1]):
            l.append(-sum(self.mrr[(self.mrr.iloc[:, i-1] != 0) & (self.mrr.iloc[:, i] == 0)].iloc[:, i-1]))
            n.append(sum(self.mrr[(self.mrr.iloc[:, i-1] == 0) & (self.mrr.iloc[:, i] != 0)].iloc[:, i]))
        self.rev_build.loc['Lost customers'] = ["NaN"] + l
        self.rev_build.loc['New customers'] = ["NaN"] + n
        self.rev_build.loc['Decrease'] = ["NaN"] + list(self.decrease_mrr.iloc[:, 1:].sum())
        self.rev_build.loc['Increase'] = ["NaN"] + list(self.upsell.iloc[:, 1:].sum())

        self.rev_build.loc['Total Additions'] = ["NaN"] + list(self.rev_build.loc['Increase'].iloc[1:]+self.rev_build.loc['New customers'].iloc[1:])
        self.rev_build.loc['Total Subtractions'] = ["NaN"] + list(self.rev_build.loc['Decrease'].iloc[1:]+self.rev_build.loc['Lost customers'].iloc[1:])

        self.rev_build.loc['Churn %'] = ["NaN"] + list(self.rev_build.loc['Total Subtractions'].iloc[1:]/self.rev_build.loc['Beginning balance'].iloc[1:])
        self.rev_build.loc['Upsell %'] = ["NaN"] + list(self.rev_build.loc['Increase'].iloc[1:]/self.rev_build.loc['Beginning balance'].iloc[1:])
        self.rev_build.loc['New customer %'] = ["NaN"] + list(self.rev_build.loc['New customers'].iloc[1:]/self.rev_build.loc['Ending'].iloc[1:])
        print(self.rev_build)
