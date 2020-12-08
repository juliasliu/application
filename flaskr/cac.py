'''Python script to generate CAC'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class CAC:

    def __init__(self, fin_perf, oper_metrics, oth_metrics):
        print("INIT CAC")
        self.fin_perf = pd.DataFrame(fin_perf)
        self.oper_metrics = pd.DataFrame(oper_metrics)
        self.oth_metrics = pd.DataFrame(oth_metrics)

    def run(self):
        self.clean_inputs()
        print(self.fin_perf)
        print(self.oper_metrics)
        print(self.oth_metrics)

        self.ttm_cac()
        self.yoy_growth()

        self.clean_outputs()
        json = {
            "CAC & CAC TTM": self.cac_ttm.to_dict(orient='records'),
            "CAC YoY Growth": self.cac_yoy.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        self.fin_perf = self.fin_perf.copy()
        self.fin_perf.set_index("Financial Performance", inplace=True)
        self.fin_perf.apply(filter_to_dec_list)
        self.oper_metrics = self.oper_metrics.copy()
        self.oper_metrics.set_index("Operating Metrics", inplace=True)
        self.oper_metrics.apply(filter_to_dec_list)
        self.oth_metrics.set_index("Other Metrics", inplace=True)
        self.oth_metrics.apply(filter_to_dec_list)

    def clean_outputs(self):
        self.cac_ttm = self.cac_ttm.astype(object)
        self.cac_ttm.apply(nan_to_blank_list)
        self.cac_ttm = self.cac_ttm.apply(numbers_with_commas_list)
        self.cac_ttm = self.cac_ttm.drop(self.cac_ttm.columns[0], axis=1)
        self.cac_ttm.reset_index(inplace=True)

        self.cac_yoy = self.cac_yoy.astype(object)
        self.cac_yoy.apply(nan_to_blank_list)
        cac_yoy_copy = self.cac_yoy.copy()
        self.cac_yoy = self.cac_yoy.apply(numbers_with_commas_list)
        self.cac_yoy.loc['YoY growth'] = cac_yoy_copy.loc['YoY growth'].apply(dec_to_percents)
        self.cac_yoy.loc['YoY growth*'] = cac_yoy_copy.loc['YoY growth*'].apply(dec_to_percents)
        self.cac_yoy = self.cac_yoy.drop(self.cac_yoy.columns[0], axis=1)
        self.cac_yoy.reset_index(inplace=True)

        print("CAC & CAC TTM")
        print(self.cac_ttm)
        print("CAC YoY Growth")
        print(self.cac_yoy)

    def ttm_cac(self):
        index = ["S&M", "Total Expense", "# of New Customers", "CAC", "TTM CAC"]
        self.cac_ttm = pd.DataFrame(index=np.arange(len(index)), columns=self.fin_perf.columns)
        self.cac_ttm.set_index(pd.Series(index, name=""), inplace=True)
        self.cac_ttm.loc['S&M'] = -self.fin_perf.loc['S&M']*1000
        self.cac_ttm.loc['Total Expense'] = self.cac_ttm.loc['S&M']
        self.cac_ttm.loc['# of New Customers'] = self.oper_metrics.loc['A']
        self.cac_ttm.loc['CAC'] = self.cac_ttm.loc['Total Expense'].div(self.cac_ttm.loc['# of New Customers'].replace({0:np.nan}))
        self.cac_ttm.loc['TTM CAC'][:12] = ["N/A"]*12
        for i in range(12, self.cac_ttm.shape[1]):
            self.cac_ttm.loc['TTM CAC'][i] = self.cac_ttm.loc['Total Expense'].iloc[i-11:i+1].sum()/self.cac_ttm.loc['# of New Customers'].iloc[i-11:i+1].sum()

    def yoy_growth(self):
        index = ["TTM CAC", "YoY growth", "Avg ARR Per Customer", "YoY growth*"]
        self.cac_yoy = pd.DataFrame(index=np.arange(len(index)), columns=self.fin_perf.columns)
        self.cac_yoy.set_index(pd.Series(index, name=""), inplace=True)
        self.cac_yoy.loc['TTM CAC'] = self.cac_ttm.loc['TTM CAC']
        self.cac_yoy.loc['YoY growth'].iloc[:min(self.cac_yoy.shape[1], 24)] = [float("NaN")]*min(self.cac_yoy.shape[1], 24)
        self.cac_yoy.loc['YoY growth*'].iloc[:min(self.cac_yoy.shape[1], 24)] = [float("NaN")]*min(self.cac_yoy.shape[1], 24)
        self.cac_yoy.loc['Avg ARR Per Customer'] = self.oth_metrics.loc['Avg ARR per Customer']
        if self.cac_yoy.shape[1] >= 24:
            self.cac_yoy.loc['YoY growth'].iloc[24:] = list(self.cac_yoy.loc['TTM CAC'].iloc[24:].array/self.cac_yoy.loc['TTM CAC'].iloc[12:-12].array-1)
            self.cac_yoy.loc['YoY growth*'].iloc[24:] = list(self.cac_yoy.loc['Avg ARR Per Customer'].iloc[24:].array/self.cac_yoy.loc['Avg ARR Per Customer'].iloc[12:-12].array-1)
