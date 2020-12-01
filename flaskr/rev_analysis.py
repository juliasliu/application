'''Python script to generate Revenue Analysis given MRR by Customer'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import sys

class RevAnalysis:

    def __init__(self, json):
        print("INIT REV ANALYSIS", file=sys.stdout)
        self.arr = pd.DataFrame(json)
        self.clean_inputs()
        print(self.arr, file=sys.stdout)

    def dollars_to_dec(self, x):
        for i in range(len(x)):
            if x[i] != '' and isinstance(x[i], str):
                x[i] = float(x[i].strip('$').strip().replace(',', ''))
            elif x[i] == '':
                x[i] = 0
        return x

    def dec_to_dollars(self, x):
        for i in range(len(x)):
            if x[i] != 0:
                x[i] = '$%.2f' % x[i]
            else:
                x[i] = ''
        return x

    def clean_inputs(self):
        self.arr.iloc[:, 1:].apply(self.dollars_to_dec)
        # print(self.arr_by_customer, file=sys.stdout)

    def clean_outputs(self):
        self.mrr.iloc[:, 1:].apply(self.dec_to_dollars)
        # print(self.arr_by_customer, file=sys.stdout)

    def mrr_by_customer(self):
        # 1. MRR BY CUSTOMER

        self.mrr = self.arr.copy()
        self.mrr.iloc[:, 1:] = self.mrr.iloc[:, 1:].apply(lambda x: x/12)
        self.clean_outputs()

        print("MRR BY CUSTOMER")
        print(self.mrr, file=sys.stdout)
        return self.mrr.to_json(orient='records')

    def rev_analysis(self):
        # 1. REV ANALYSIS
        print("REVENUE ANALYSIS")
        rev_analysis_final = self.data/12

        print(rev_analysis_final, file=sys.stdout)
        return rev_analysis_final.to_json(orient='records')
