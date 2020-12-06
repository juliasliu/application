'''Python script to generate Cohort Analysis'''
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
        self.missing_months = []

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
        self.mrr.apply(dollars_to_dec_list)
        self.cohorts.set_index("Customer", inplace=True)
        self.cohorts.iloc[:, 1:] = self.cohorts.iloc[:, 1:].apply(dollars_to_dec_list)

    def clean_outputs(self):
        cohort_months = list(pd.to_datetime(self.rev_cohorts.index).strftime('%m/%Y'))
        years = [m.split("/")[1] for m in cohort_months]
        counter = collections.Counter(years)
        all_months = []
        for year in counter.keys():
            all_months.extend(["{:02d}".format(i+1)+"/"+year for i in range(12)])
        all_months.pop(0)
        self.missing_months = list(set(all_months) - set(cohort_months))
        last_month = str_to_datetime(cohort_months[-1])
        self.missing_months = list(filter(lambda m: str_to_datetime(m) <= last_month, self.missing_months))

        self.clean_outputs_add_empty_rows(self.rev_cohorts)
        self.clean_outputs_add_empty_rows(self.cust_cohorts)
        self.clean_outputs_add_empty_rows(self.rev_retention)
        self.clean_outputs_add_empty_rows(self.logo_retention)
        self.clean_outputs_add_empty_rows(self.cumulative)

        col_labels_dict = {col: "M"+str(col+1) for col in self.rev_cohorts.columns}

        self.retention_statistics(self.rev_retention)
        self.retention_statistics(self.logo_retention)
        self.retention_statistics(self.cumulative)

        indices = [i for i in range(self.cumulative.shape[1]) if "# Customers" != self.cumulative.columns[i]]

        self.rev_cohorts = self.rev_cohorts.astype(object)
        self.rev_cohorts.apply(na_to_zero_list)
        self.rev_cohorts.apply(zero_to_blank_list)
        self.rev_cohorts.apply(dec_to_dollars_list)
        self.rev_cohorts.reset_index(inplace=True)
        self.rev_cohorts.rename(columns=col_labels_dict, inplace=True)

        self.cust_cohorts = self.cust_cohorts.astype(object)
        self.cust_cohorts.apply(na_to_zero_list)
        self.cust_cohorts.apply(zero_to_blank_list)
        self.cust_cohorts.apply(numbers_with_commas_list)
        self.cust_cohorts.reset_index(inplace=True)
        self.cust_cohorts.rename(columns=col_labels_dict, inplace=True)

        self.rev_retention = self.rev_retention.astype(object)
        self.rev_retention.apply(na_to_zero_list)
        self.rev_retention.apply(zero_to_blank_list)
        self.rev_retention.iloc[:, indices] = self.rev_retention.iloc[:, indices].apply(dec_to_percents_list)
        self.rev_retention = self.rev_retention.reindex(['# Customers'] + list(self.cumulative.columns[:-1]), axis=1)
        self.rev_retention.reset_index(inplace=True)
        self.rev_retention.rename(columns=col_labels_dict, inplace=True)

        self.logo_retention = self.logo_retention.astype(object)
        self.logo_retention.apply(na_to_zero_list)
        self.logo_retention.apply(zero_to_blank_list)
        self.logo_retention.iloc[:, indices] = self.logo_retention.iloc[:, indices].apply(dec_to_percents_list)
        self.logo_retention = self.logo_retention.reindex(['# Customers'] + list(self.cumulative.columns[:-1]), axis=1)
        self.logo_retention.reset_index(inplace=True)
        self.logo_retention.rename(columns=col_labels_dict, inplace=True)

        self.cumulative = self.cumulative.astype(object)
        self.cumulative.apply(na_to_zero_list)
        self.cumulative.apply(zero_to_blank_list)
        self.cumulative.iloc[:, indices] = self.cumulative.iloc[:, indices].apply(dec_to_dollars_list)
        self.cumulative = self.cumulative.reindex(['# Customers'] + list(self.cumulative.columns[:-1]), axis=1)
        self.cumulative.reset_index(inplace=True)
        self.cumulative.rename(columns=col_labels_dict, inplace=True)

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

    def clean_outputs_add_empty_rows(self, data):
        for m in self.missing_months:
            data.loc[str_to_datetime(m)] = ['NaN'] * data.shape[1]
        data.sort_index(inplace=True)
        data.index = pd.to_datetime(data.index).strftime('%m/%Y')

    def revenue_cohorts(self):
        self.mrr_cohorts = self.mrr.copy()
        self.mrr_cohorts = self.mrr_cohorts.iloc[:, 1:]
        self.mrr_cohorts.columns = pd.to_datetime(self.mrr_cohorts.columns).strftime('%m/%Y')
        self.mrr_cohorts['Cohort'] = pd.to_datetime(self.cohorts['Cohort'])
        self.rev_cohorts = self.mrr_cohorts.groupby(by=['Cohort']).sum()
        self.rev_cohorts = self.rev_cohorts.iloc[1:]
        self.rev_cohorts.sort_values('Cohort')
        self.rev_cohorts = self.rev_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.rev_cohorts.set_axis(self.rev_cohorts.columns[self.rev_cohorts.columns], axis=1, inplace=False)

    def customer_cohorts(self):
        self.cust_cohorts = self.mrr_cohorts.groupby(by=['Cohort']).agg(lambda x: x.ne(0).sum())
        self.cust_cohorts = self.cust_cohorts.iloc[1:]
        self.cust_cohorts.sort_values('Cohort')
        self.cust_cohorts = self.cust_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.cust_cohorts.set_axis(self.cust_cohorts.columns[self.cust_cohorts.columns], axis=1, inplace=False)

    def revenue_retention(self):
        self.rev_retention = pd.DataFrame(index=np.arange(self.rev_cohorts.shape[0]))
        self.rev_retention.set_index(self.rev_cohorts.index, inplace=True)
        self.rev_retention = self.rev_cohorts.apply(lambda x: x/x.iloc[0], axis=1)

    def logo_retention(self):
        self.logo_retention = pd.DataFrame(index=np.arange(self.cust_cohorts.shape[0]))
        self.logo_retention.set_index(self.cust_cohorts.index, inplace=True)
        self.logo_retention = self.cust_cohorts.apply(lambda x: x/x.iloc[0], axis=1)

    def cumulative(self):
        self.cumulative = self.rev_cohorts.copy()
        self.cumulative = self.cumulative.apply(pd.DataFrame.cumsum, axis=1)
        self.cumulative['# Customers'] = self.cust_cohorts.iloc[:, 0]
        self.cumulative = self.cumulative.apply(lambda x: x/x.loc['# Customers'], axis=1)

    def retention_statistics(self, data):
        data_copy = data.astype('float64')
        data.loc["Min"] = data_copy[data_copy != "NaN"].min()
        data.loc["25th Percentile"] = data_copy.quantile(0.25)
        data.loc["Median"] = data_copy[data_copy != "NaN"].median()
        data.loc["Mean"] = data_copy[data_copy != "NaN"].mean()
        data.loc["75th Percentile"] = data_copy.quantile(0.75)
        data.loc["Max"] = data_copy[data_copy != "NaN"].max()
        data['# Customers'] = self.cust_cohorts.iloc[:, 0]
