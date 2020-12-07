'''Python script to generate Revenue Analysis given ARR by Customer'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class RevAnalysis:

    def __init__(self, json):
        print("INIT REV ANALYSIS")
        self.arr = pd.DataFrame(json)
        self.years = []
        self.rev_brackets = {}
        self.cust_brackets = {}

    def run(self):
        self.clean_inputs()
        print(self.arr)

        self.mrr_by_customer()
        self.rev_cohorts()
        self.cy_ttm_revenue()
        self.revenue_brackets("CY", "TTM")
        self.customer_brackets("CY", "TTM")
        self.revenue_brackets("ARR", "ARR*")
        self.customer_brackets("ARR", "ARR*")

        self.clean_outputs()
        json = {
            "MRR by Customer": self.mrr.to_dict(orient='records'),
            "Revenue Cohorts (Monthly)": self.rev_cohorts.to_dict(orient='records'),
            "Revenue Calculations": self.cy_ttm_revenue.to_dict(orient='records'),
            "Revenue Brackets (CY, TTM)": self.rev_brackets["CY"].to_dict(orient='records'),
            "Customer Brackets (CY, TTM)": self.cust_brackets["CY"].to_dict(orient='records'),
            "Revenue Brackets (ARR)": self.rev_brackets["ARR"].to_dict(orient='records'),
            "Customer Brackets (ARR)": self.cust_brackets["ARR"].to_dict(orient='records')
        }
        return json

    def clean_inputs(self):
        self.arr.set_index("Customer", inplace=True)
        self.arr.apply(filter_to_dec_list)

    def clean_outputs(self):
        self.mrr = self.mrr.astype(object)
        self.mrr.apply(zero_to_blank_list)
        self.mrr.apply(dec_to_dollars_list)
        self.mrr.reset_index(inplace=True)

        self.rev_cohorts = self.rev_cohorts.astype(object)
        self.rev_cohorts.iloc[:, 1:-1] = self.rev_cohorts.iloc[:, 1:-1].apply(zero_to_blank_list)
        self.rev_cohorts.iloc[:, 1:-1] = self.rev_cohorts.iloc[:, 1:-1].apply(dec_to_dollars_list)
        self.rev_cohorts.reset_index(inplace=True)

        cy = [col for col in self.cy_ttm_revenue.columns if "CY" in col and "YOY" not in col]
        ttm = [col for col in self.cy_ttm_revenue.columns if "TTM" in col]
        yoy = [col for col in self.cy_ttm_revenue.columns if "YOY" in col]
        yoy_indices = [i for i in range(self.cy_ttm_revenue.shape[1]) if "YOY" in self.cy_ttm_revenue.columns[i] or "Total ARR" in self.cy_ttm_revenue.columns[i]]
        not_yoy_indices = list(set(range(self.cy_ttm_revenue.shape[1])) - set(yoy_indices))
        arr = [col for col in self.cy_ttm_revenue.columns if "ARR" in col]
        self.cy_ttm_revenue = self.cy_ttm_revenue.astype(object)
        self.cy_ttm_revenue.apply(zero_to_blank_list)
        self.cy_ttm_revenue.iloc[:, not_yoy_indices] = self.cy_ttm_revenue.iloc[:, not_yoy_indices].apply(dec_to_dollars_list)
        self.cy_ttm_revenue.iloc[:, yoy_indices] = self.cy_ttm_revenue.iloc[:, yoy_indices].apply(dec_to_percents_list)
        self.cy_ttm_revenue.sort_values(self.cy_ttm_revenue.columns[-1])
        self.cy_ttm_revenue = self.cy_ttm_revenue.reindex(cy + ttm + yoy + arr, axis=1)
        self.cy_ttm_revenue.reset_index(inplace=True)

        self.clean_brackets_outputs("CY", "TTM")
        self.clean_brackets_outputs("ARR", "ARR*")

        print("MRR BY CUSTOMER")
        print(self.mrr)
        print("REVENUE COHORTS")
        print(self.rev_cohorts)
        print("CY TTM ARR")
        print(self.cy_ttm_revenue)
        print("CY TTM BRACKETS")
        print(self.rev_brackets["CY"])
        print("REVENUE CUSTOMER BRACKETS")
        print(self.cust_brackets["CY"])
        print("ARR BRACKETS")
        print(self.rev_brackets["ARR"])
        print("ARR CUSTOMER BRACKETS")
        print(self.cust_brackets["ARR"])

    def clean_brackets_outputs(self, type, not_type):
        cy_only = [col for col in self.rev_brackets[type].columns if type in col and not_type not in col and "% Rev" not in col]
        cy_rev = [col for col in self.rev_brackets[type].columns if "% Rev" in col and not_type not in col]
        new_cy = [j for i in zip(cy_only,cy_rev) for j in i]
        ttm_all = [col for col in self.rev_brackets[type].columns if not_type in col]
        rev_indices = [i for i in range(self.rev_brackets[type].shape[1]) if "% Rev" in self.rev_brackets[type].columns[i]]
        not_rev_indices = list(set(range(self.rev_brackets[type].shape[1])) - set(rev_indices))
        self.rev_brackets[type] = self.rev_brackets[type].astype(object)
        self.rev_brackets[type].iloc[:, not_rev_indices] = self.rev_brackets[type].iloc[:, not_rev_indices].apply(numbers_with_commas_list)
        self.rev_brackets[type].iloc[:, rev_indices] = self.rev_brackets[type].iloc[:, rev_indices].apply(dec_to_percents_list)
        self.rev_brackets[type] = self.rev_brackets[type].reindex(new_cy + ttm_all, axis=1)
        self.rev_brackets[type].index = self.rev_brackets[type].index.map(dec_to_dollars)
        self.rev_brackets[type].reset_index(inplace=True)

        self.cust_brackets[type] = self.cust_brackets[type].astype(object)
        self.cust_brackets[type].apply(numbers_with_commas_list)
        self.cust_brackets[type].index = self.cust_brackets[type].index.map(dec_to_dollars)
        cust_brackets_index = self.cust_brackets[type].index
        index_labels_dict = {cust_brackets_index[i]: str(cust_brackets_index[i])+"-"+str(cust_brackets_index[i+1]) for i in range(len(cust_brackets_index)-1)}
        index_labels_dict[cust_brackets_index[-1]] = str(cust_brackets_index[-1])+'+'
        self.cust_brackets[type].rename(index=index_labels_dict, inplace=True)
        self.cust_brackets[type].reset_index(inplace=True)

    def mrr_by_customer(self):
        self.mrr = self.arr.copy()/12
        self.mrr.loc["ARR"] = (self.mrr.iloc[-1:]*12).iloc[0]

        # Only keep the last 3 years
        self.years = pd.to_datetime(self.mrr.columns).strftime('%Y')
        counter = collections.Counter(self.years)
        num_trailing_months = counter[max(counter.keys())]
        del counter[max(counter.keys())]
        last_index = min(36, 12*len(counter.keys())) + num_trailing_months
        self.mrr = self.mrr.iloc[:, -last_index:]
        self.years = pd.to_datetime(self.mrr.columns).strftime('%Y')

    def rev_cohorts(self):
        first_rev = np.argmax(self.mrr.values!=0.0,axis=1)
        last_rev = self.mrr.shape[1] - np.argmax(self.mrr.iloc[:, ::-1].values!=0.0,axis=1) - 1

        self.rev_cohorts = pd.DataFrame(index=np.arange(self.mrr.shape[0]))
        self.rev_cohorts.set_index(self.mrr.index, inplace=True)
        self.rev_cohorts['Cohort'] = self.mrr.columns[first_rev]
        self.rev_cohorts['Cohort'] = pd.to_datetime(self.rev_cohorts['Cohort']).dt.strftime('%m/%Y')
        self.rev_cohorts['Initial Rev'] = [self.mrr.iloc[i][first_rev[i]] for i in range(len(first_rev))]
        self.rev_cohorts['End Rev'] = [self.mrr.iloc[i][last_rev[i]] for i in range(len(last_rev))]
        self.rev_cohorts['End'] = self.mrr.columns[last_rev]
        self.rev_cohorts['End'] = pd.to_datetime(self.rev_cohorts['End']).dt.strftime('%m/%Y')
        self.rev_cohorts = self.rev_cohorts.apply(lambda x: ["N/A"]+list(x.iloc[1:-1])+["N/A"] if (x['Initial Rev']==0 and x['End Rev']==0) else x, axis=1)

        self.rev_cohorts.drop(self.rev_cohorts.tail(2).index, inplace=True)

    def cy_ttm_revenue(self):
        self.cy_ttm_revenue = pd.DataFrame(index=np.arange(self.mrr.shape[0]))
        self.cy_ttm_revenue.set_index(self.mrr.index, inplace=True)

        counter = collections.Counter(self.years)
        for year in counter.keys():
            if counter[year] == 12:
                # Calculate CY for each full year
                current_year_indices = [i for i in range(len(self.years)) if self.years[i] == year]
                current_year_columns = self.mrr.iloc[:,current_year_indices]
                self.cy_ttm_revenue["CY "+year] = current_year_columns.sum(axis=1)
                # Calculate ARRs for the last month of each full year
                self.cy_ttm_revenue["12/"+year+" ARR"] = current_year_columns.iloc[:, -1:]*12

        # Calculate TTM for the last month
        mrr_ttm = self.mrr.iloc[:, -12:]
        self.cy_ttm_revenue["TTM "+pd.to_datetime(mrr_ttm.columns[-1]).strftime('%m/%Y')] = mrr_ttm.sum(axis=1)
        # Calculate ARR for the last month
        self.cy_ttm_revenue[pd.to_datetime(mrr_ttm.columns[-1]).strftime('%m/%Y')+" ARR*"] = mrr_ttm.iloc[:, -1:]*12
        # Calculate % of Total ARR for last month
        self.cy_ttm_revenue["% Total ARR"] = mrr_ttm.iloc[:, -1:]*12/mrr_ttm.loc["ARR"].iloc[-1]

        # Calculate CY YoY for each pair of CYs
        cy_labels = [label for label in self.cy_ttm_revenue.columns if "CY" in label]
        cy_columns = self.cy_ttm_revenue.loc[:,cy_labels]
        for i in range(1, cy_columns.shape[1]):
            prev_cy = pd.Series(cy_columns.iloc[:, i-1])
            curr_cy = pd.Series(cy_columns.iloc[:, i])
            yoy = [(curr_cy[j]/prev_cy[j]-1 if prev_cy[j] != 0 else 0) for j in range(len(prev_cy))]
            self.cy_ttm_revenue[cy_columns.columns[i]+" YOY"] = yoy

        self.cy_ttm_revenue.drop(self.cy_ttm_revenue.tail(1).index, inplace=True)

    def revenue_brackets(self, type, not_type):
        brackets = [0, 10000, 50000, 100000, 250000, 500000, 750000, 1000000, 1500000, 2000000, 3000000, 4000000]
        self.rev_brackets[type] = pd.DataFrame(index=np.arange(len(brackets)))
        self.rev_brackets[type].set_index(pd.Series(brackets, name=''), inplace=True)

        # Create columns
        cy_labels = [col for col in self.cy_ttm_revenue.columns if type in col and not_type not in col and "YOY" not in col and "Total" not in col]
        cy_columns = self.cy_ttm_revenue.loc[:,cy_labels]
        for cy in cy_columns:
            self.rev_brackets[type][cy] = pd.Series()
        for cy in cy_columns:
            self.rev_brackets[type]['% Rev '+cy] = pd.Series()

        ttm = [col for col in self.cy_ttm_revenue.columns if not_type in col][0]
        ttm_column = self.cy_ttm_revenue[ttm]
        self.rev_brackets[type][ttm] = pd.Series()
        self.rev_brackets[type]['% Rev '+ttm] = pd.Series()

        for b in brackets:
            # Count how many companies fall in each bracket for CY
            cy_counts = cy_columns.apply(lambda x: x.iloc[:-1].apply(lambda y: y >= b and y > 0)).sum()
            # Calculate % revenue for each CY bracket
            cy_rev_percents = cy_columns.apply(lambda x: x.iloc[:-1][x.iloc[:-1].apply(lambda y: y >= b and y > 0)].sum()/x.iloc[-1])
            # Count how many companies fall in each bracket for TTM
            ttm_counts = ttm_column.iloc[:-1].apply(lambda y: y >= b and y > 0).sum()
            # Calculate % revenue for each TTM bracket
            ttm_rev_percents = ttm_column.iloc[:-1][ttm_column.iloc[:-1].apply(lambda y: y >= b and y > 0)].sum()/ttm_column.iloc[-1]

            cy_data = list(cy_counts.values) + list(cy_rev_percents.values) + [ttm_counts] + [ttm_rev_percents]
            self.rev_brackets[type].loc[b] = cy_data

    def customer_brackets(self, type, not_type):
        self.cust_brackets[type] = pd.DataFrame(index=np.arange(self.rev_brackets[type].shape[0]))
        self.cust_brackets[type].set_index(pd.Series(self.rev_brackets[type].index, name='Customer Type'), inplace=True)

        ttm = [col for col in self.rev_brackets[type].columns if not_type in col][0]
        ttm_column = list(self.rev_brackets[type][ttm])
        self.cust_brackets[type]['# Customers'] = [ttm_column[i-1] - ttm_column[i] for i in range(1, self.cust_brackets[type].shape[0])] + [0]
