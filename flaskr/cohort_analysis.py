'''Python script to generate cohort analysis spreadsheets based on SEMrush inputs'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class CohortAnalysis:

    def __init__(self, mrr, cohorts):
        print("INIT COHORT ANALYSIS")
        self.mrr = pd.DataFrame(mrr)
        self.cohorts = pd.DataFrame(cohorts)

    def run(self):
        self.clean_inputs()
        print(self.mrr)
        print(self.cohorts)

        self.revenue_cohorts()
        self.customer_cohorts()
        self.revenue_retention()
        self.logo_retention()
        self.cumulative()

        self.clean_outputs()
        json = {
            "Revenue Cohorts Calculation (Monthly)": self.rev_cohorts.to_dict(orient='records'),
            "Customer Cohorts Calculation (Monthly)": self.cust_cohorts.to_dict(orient='records'),
            "Revenue Retention (Monthly)": self.rev_retention.to_dict(orient='records'),
            "Logo Retention (Monthly)": self.logo_retention.to_dict(orient='records'),
            "Cumulative Revenue Per Customer (Monthly)": self.cumulative.to_dict(orient='records')
        }
        return json

    def clean_inputs(self):
        self.mrr.set_index("Customer", inplace=True)
        self.mrr.apply(dollars_to_dec)
        self.cohorts.set_index("Customer", inplace=True)
        self.cohorts.iloc[:, 1:] = self.cohorts.iloc[:, 1:].apply(dollars_to_dec)

    def clean_outputs(self):
        self.rev_cohorts[0] = pd.to_datetime(self.rev_cohorts[0]).dt.strftime('%m/%Y')
        self.rev_cohorts.iloc[:, 1:] = self.rev_cohorts.iloc[:, 1:].apply(na_to_zero)
        self.rev_cohorts.iloc[:, 1:] = self.rev_cohorts.iloc[:, 1:].apply(dec_to_dollars)

        self.cust_cohorts[0] = pd.to_datetime(self.cust_cohorts[0]).dt.strftime('%m/%Y')
        self.cust_cohorts.iloc[:, 1:] = self.cust_cohorts.iloc[:, 1:].apply(na_to_zero)
        self.cust_cohorts.iloc[:, 1:] = self.cust_cohorts.iloc[:, 1:].apply(zero_to_blank)

        self.rev_retention[0] = pd.to_datetime(self.rev_retention[0]).dt.strftime('%m/%Y')
        self.rev_retention.iloc[:, 1:] = self.rev_retention.iloc[:, 1:].apply(na_to_zero)
        self.rev_retention.iloc[:, 1:] = self.rev_retention.iloc[:, 1:].apply(dec_to_percents)

        self.logo_retention[0] = pd.to_datetime(self.logo_retention[0]).dt.strftime('%m/%Y')
        self.logo_retention.iloc[:, 1:] = self.logo_retention.iloc[:, 1:].apply(na_to_zero)
        self.logo_retention.iloc[:, 1:] = self.logo_retention.iloc[:, 1:].apply(dec_to_percents)

        self.cumulative[0] = pd.to_datetime(self.cumulative[0]).dt.strftime('%m/%Y')
        indices = [i for i in range(self.cumulative.shape[1]) if "# Customers" != self.cumulative.columns[i] and i!=0]
        self.cumulative.iloc[:, 1:] = self.cumulative.iloc[:, 1:].apply(na_to_zero)
        self.cumulative.iloc[:, indices] = self.cumulative.iloc[:, indices].apply(dec_to_dollars)
        self.cumulative = self.cumulative.reindex(['# Customers'] + list(self.cumulative.columns[:-1]), axis=1)

        print("REVENUE COHORTS")
        print(self.rev_cohorts)
        print("CUSTOMER COHORTS")
        print(self.cust_cohorts)
        print("REVENUE RETENTION")
        print(self.rev_retention)
        print("LOGO RETENTION")
        print(self.logo_retention)
        print("CUMULATIVE")
        print(self.cumulative)

    def revenue_cohorts(self):
        self.mrr_cohorts = self.mrr.copy()
        self.mrr_cohorts.columns = pd.to_datetime(self.mrr_cohorts.columns).strftime('%m/%Y')
        self.mrr_cohorts['Cohort'] = pd.to_datetime(self.cohorts['Cohort'])
        self.rev_cohorts = self.mrr_cohorts.groupby(by=['Cohort'], as_index=False).sum()
        self.rev_cohorts.sort_values("Cohort")
        self.rev_cohorts = self.rev_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.rev_cohorts.set_axis(self.rev_cohorts.columns[self.rev_cohorts.columns], axis=1, inplace=False)

    def customer_cohorts(self):
        self.cust_cohorts = self.mrr_cohorts.groupby(by=['Cohort'], as_index=False).agg(lambda x: x.ne(0).sum())
        self.cust_cohorts.sort_values("Cohort")
        self.cust_cohorts = self.cust_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.cust_cohorts.set_axis(self.cust_cohorts.columns[self.cust_cohorts.columns], axis=1, inplace=False)

    def revenue_retention(self):
        self.rev_retention = self.rev_cohorts.copy()
        self.rev_retention.iloc[:, 1:] = self.rev_retention.iloc[:, 1:].apply(lambda x: x/x.iloc[0], axis=1)

    def logo_retention(self):
        self.logo_retention = self.cust_cohorts.copy()
        self.logo_retention.iloc[:, 1:] = self.logo_retention.iloc[:, 1:].apply(lambda x: x/x.iloc[0], axis=1)

    def cumulative(self):
        self.cumulative = self.rev_cohorts.copy()
        self.cumulative.iloc[:, 1:] = self.cumulative.iloc[:, 1:].apply(pd.DataFrame.cumsum, axis=1)
        self.cumulative['# Customers'] = self.cust_cohorts.iloc[:, 1]
        self.cumulative.iloc[:, 1:] = self.cumulative.iloc[:, 1:].apply(lambda x: x/x.loc['# Customers'], axis=1)
        self.cumulative['# Customers'] = self.cust_cohorts.iloc[:, 1]
