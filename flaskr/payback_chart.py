'''Python script to generate Payback Chart (Monthly)'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class PaybackChart:

    def __init__(self, rev_cohorts, cumulative, oper_stats, cac, missing_months):
        print("INIT PAYBACK CHART")
        self.rev_cohorts = pd.DataFrame(rev_cohorts)
        self.cumulative = pd.DataFrame(cumulative)
        self.oper_stats = pd.DataFrame(oper_stats)
        self.cac = pd.DataFrame(cac)
        self.missing_months = missing_months

    def run(self):
        self.clean_inputs()
        print(self.rev_cohorts)
        print(self.cumulative)
        print(self.oper_stats)
        print(self.cac)

        self.cm_by_month()
        self.cumulative_cm_per_customer()
        self.sm_by_month()
        self.sm_per_customer()
        self.contribution_margin_sm()

        self.clean_outputs()
        json = {
            "CM by Month": self.cm.to_dict(orient='records'),
            "Cumulative CM per Customer by Month": self.cumulative_cm_per.to_dict(orient='records'),
            "S&M by Month": self.sm.to_dict(orient='records'),
            "S&M by Month per Customer per Cohort": self.sm_per.to_dict(orient='records'),
            "Contribution Margin / S&M": self.cm_sm.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        self.rev_cohorts = self.rev_cohorts.copy()
        self.rev_cohorts.set_index("Cohort", inplace=True)
        self.rev_cohorts.apply(filter_to_dec_list)
        self.cumulative = self.cumulative.copy()
        self.cumulative.set_index("Cohort", inplace=True)
        self.cumulative.apply(filter_to_dec_list)
        self.cumulative.drop(self.cumulative.tail(6).index, inplace=True)
        self.oper_stats = self.oper_stats.copy()
        self.oper_stats.set_index("Operating Statistics", inplace=True)
        self.oper_stats = self.oper_stats.iloc[:, 1:]
        self.oper_stats.apply(filter_to_dec_list)
        self.cac = self.cac.copy()
        self.cac.set_index(self.cac.columns[0], inplace=True)
        self.cac.apply(filter_to_dec_list)

    def clean_outputs(self):
        col_labels_dict = {col: "M"+str(col+1) for col in self.sm.columns}

        self.cm = self.cm.astype(object)
        self.cm.apply(nan_to_blank_list)
        self.cm = self.cm.apply(numbers_with_commas_list)
        self.cm.rename(columns=col_labels_dict, inplace=True)
        self.cm.reset_index(inplace=True)

        self.cumulative_cm_per = self.cumulative_cm_per.astype(object)
        self.cumulative_cm_per.apply(nan_to_blank_list)
        self.cumulative_cm_per = self.cumulative_cm_per.apply(numbers_with_commas_list)
        self.cumulative_cm_per.rename(columns=col_labels_dict, inplace=True)
        self.cumulative_cm_per.reset_index(inplace=True)

        self.sm = self.sm.astype(object)
        self.sm.apply(nan_to_blank_list)
        self.sm = self.sm.apply(numbers_with_commas_list)
        self.sm.reset_index(inplace=True)
        self.sm.rename(columns=col_labels_dict, inplace=True)

        self.sm_per = self.sm_per.astype(object)
        self.sm_per.apply(nan_to_blank_list)
        self.sm_per = self.sm_per.apply(numbers_with_commas_list)
        self.sm_per.rename(columns=col_labels_dict, inplace=True)
        self.sm_per = self.sm_per.reindex(['# Customers'] + list(self.sm_per.columns[:-1]), axis=1)
        self.sm_per.reset_index(inplace=True)

        self.cm_sm = self.cm_sm.astype(object)
        self.cm_sm.apply(nan_to_blank_list)
        self.cm_sm = self.cm_sm.apply(dec_to_hundredths_list)
        self.cm_sm['# Customers'] = self.cumulative['# Customers']
        self.cm_sm.apply(nan_to_blank_list)
        self.cm_sm.rename(columns=col_labels_dict, inplace=True)
        self.cm_sm = self.cm_sm.reindex(['# Customers'] + list(self.cm_sm.columns[:-1]), axis=1)
        self.cm_sm.reset_index(inplace=True)

        print("CM by month")
        print(self.cm)
        print("Cumulative CM per customer by month")
        print(self.cumulative_cm_per)
        print("S&M by month")
        print(self.sm)
        print("S&M by month per customer per cohort")
        print(self.sm_per)
        print("Contribution Margin / S&M")
        print(self.cm_sm)

    def cm_by_month(self):
        self.cm = self.rev_cohorts.copy()
        for i in range(self.cm.shape[0]):
            self.cm.iloc[i] = pd.Series([float("NaN")]*i + [self.cm.iloc[i,j-i]*self.oper_stats.loc["Recurring Revenue Contribution Margin", self.oper_stats.columns[j]] for j in range(i, self.oper_stats.shape[1])], self.cm.columns)
        self.cm = self.cm.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.cm.set_axis(self.cm.columns[self.cm.columns], axis=1, inplace=False)
        self.cm[self.cm.shape[1]] = pd.Series([0]*self.cm.shape[0])

    def cumulative_cm_per_customer(self):
        self.cumulative_cm_per = self.cumulative.copy()
        self.cumulative_cm_per = pd.concat([self.cumulative_cm_per.loc[:, '# Customers'], self.cm.apply(pd.DataFrame.cumsum, axis=1)], axis=1)
        self.cumulative_cm_per = self.cumulative_cm_per.apply(lambda x: x/(x.loc['# Customers'] if x.loc['# Customers']!=0 else np.nan), axis=1)
        self.cumulative_cm_per['# Customers'] = self.cumulative['# Customers']

    def sm_by_month(self):
        self.sm = self.rev_cohorts.copy()
        for i in range(self.sm.shape[0]):
            self.sm.iloc[i] = pd.Series([float("NaN")]*i + [(self.cac.loc["Total Expense", self.cac.columns[j]] if self.sm.iloc[i,j-i]!=0 else 0) for j in range(i, self.cac.shape[1])], self.sm.columns)
        self.sm_raw = self.sm.copy()
        self.sm = self.sm.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.sm.set_axis(self.sm.columns[self.sm.columns], axis=1, inplace=False)
        self.sm[self.sm.shape[1]] = pd.Series([0]*self.sm.shape[0])

    def sm_per_customer(self):
        self.sm_per = self.sm.copy()
        for i in range(self.sm_per.shape[0]):
            self.sm_per.iloc[i] = pd.Series([float("NaN")]*i + [self.sm.iloc[i, 0]/self.cumulative.iloc[i].loc['# Customers'] if self.cumulative.iloc[i].loc['# Customers']!=0 else "N/A"]*(self.sm_per.shape[1]-i), self.sm_per.columns)
        self.sm_per = self.sm_per.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        self.sm_per.set_axis(self.sm_per.columns[self.sm_per.columns], axis=1, inplace=False)
        self.sm_per['# Customers'] = self.cumulative['# Customers']

    def contribution_margin_sm(self):
        self.cm_sm = self.cumulative_cm_per.div(self.sm_per.replace({0: np.nan}))
        cm_sm_copy = self.cm_sm.astype('float64')
        self.cm_sm.loc["Median"] = cm_sm_copy[cm_sm_copy != "NaN"].median()
        self.cm_sm.loc["Mean"] = cm_sm_copy[cm_sm_copy != "NaN"].mean()
