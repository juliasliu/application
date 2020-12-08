'''Python script to generate Rev Charts'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class RevCharts:

    def __init__(self, rev_build):
        print("INIT REV CHARTS")
        self.rev_build = pd.DataFrame(rev_build)

    def run(self):
        self.clean_inputs()
        print(self.rev_build)

        self.rev_chart()

        self.clean_outputs()
        json = {
            "Rev Chart": self.rev.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        self.rev_build = self.rev_build.copy()
        self.rev_build.set_index("Total MRR", inplace=True)
        self.rev_build.apply(filter_to_dec_list)

    def clean_outputs(self):
        self.rev = self.rev.astype(object)
        self.rev.apply(nan_to_blank_list)
        self.rev.apply(zero_to_blank_list)
        self.rev = self.rev.apply(numbers_with_commas_list)
        self.rev.reset_index(inplace=True)

        print("Rev chart")
        print(self.rev)

    def flatten(self, list):
        return [item for sublist in list for item in sublist]

    def rev_chart(self):
        chart_columns = []
        for month in self.rev_build.columns:
            chart_columns.extend([month, month+"*", month+"**", month+"***", month+"****"])
        chart_index = ["Offset 1", "Offset 2", "Offset 3", "Offset 4", "Beginning balance", "Lost customers", "Decrease", "Increase", "New customers", "Ending"]
        self.rev = pd.DataFrame(index=np.arange(len(chart_index)), columns=chart_columns)
        self.rev.set_index(pd.Series(chart_index, name='Total Customers'), inplace=True)
        self.rev.loc["Beginning balance"] = self.flatten([[self.rev_build.loc["Beginning MRR"][i]]+[float("NaN")]*4 for i in range(self.rev_build.shape[1])])
        self.rev.loc["Lost customers"] = self.flatten([[float("NaN")]*1+[-self.rev_build.loc["Lost customers"][i]]+[float("NaN")]*3 for i in range(self.rev_build.shape[1])])
        self.rev.loc["Decrease"] = self.flatten([[float("NaN")]*2+[-self.rev_build.loc["Decrease"][i]]+[float("NaN")]*2 for i in range(self.rev_build.shape[1])])
        self.rev.loc["Increase"] = self.flatten([[float("NaN")]*3+[self.rev_build.loc["Increase"][i]]+[float("NaN")]*1 for i in range(self.rev_build.shape[1])])
        self.rev.loc["New customers"] = self.flatten([[float("NaN")]*4+[self.rev_build.loc["New customers"][i]] for i in range(self.rev_build.shape[1])])
        self.rev.loc["Ending"] = self.flatten([[self.rev_build.loc["Ending MRR"][i]]*5 for i in range(self.rev_build.shape[1])])
        self.rev.loc["Offset 1"] = [float("NaN")]+list(self.rev.loc["Beginning balance"].iloc[:-1].array-self.rev.loc["Lost customers"].iloc[1:].array)
        self.rev.loc["Offset 2"] = [float("NaN")]*2+list(self.rev.loc["Beginning balance"].iloc[:-2].array-self.rev.loc["Decrease"].iloc[2:].array)
        self.rev.loc["Offset 3"] = [float("NaN")]+list(self.rev.loc["Offset 2"].iloc[:-1])
        self.rev.loc["Offset 4"] = [float("NaN")]+list(self.rev.loc["Offset 3"].iloc[:-1].array+self.rev.loc["Increase"].iloc[:-1].array)
