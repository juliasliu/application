'''Python script to generate Dashboard'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime
import collections

from .helpers import *

class Dashboard:

    def __init__(self, mrr, cohorts, is_dict, bs_dict, cf_dict):
        print("INIT DASHBOARD")
        self.mrr = pd.DataFrame(mrr)
        self.cohorts = pd.DataFrame(cohorts)
        self.income_stat, self.balance_sh, self.cash_flow = {}, {}, {}
        for year in is_dict.keys():
            self.income_stat[year] = pd.DataFrame(is_dict[year])
            self.balance_sh[year] = pd.DataFrame(bs_dict[year])
            self.cash_flow[year] = pd.DataFrame(cf_dict[year])

    def run(self):
        self.clean_inputs()
        print(self.mrr)
        print(self.cohorts)
        print(self.income_stat)
        print(self.balance_sh)
        print(self.cash_flow)

        self.base_build_support()
        self.rev_build_support()
        self.operating_metrics()
        self.financial_performance()
        self.operating_statistics()
        self.balance_sheet()
        self.cash_flow_statement()
        self.other_metrics()

        self.clean_outputs()
        json = {
            "BASE Build Support": self.base_build.to_dict(orient='records'),
            "Rev Build Support": self.rev_build.to_dict(orient='records'),
            "Financial Performance": self.fin_perf.to_dict(orient='records'),
            "Operating Statistics": self.oper_stats.to_dict(orient='records'),
            "Operating Metrics": self.oper_metrics.to_dict(orient='records'),
            "Balance Sheet": self.bal_sheet.to_dict(orient='records'),
            "Cash Flow Statement": self.cash_flow_stat.to_dict(orient='records'),
            "Other Metrics": self.oth_metrics.to_dict(orient='records'),
        }
        return json

    def clean_inputs(self):
        self.mrr = self.mrr.copy()
        self.mrr.set_index("Customer", inplace=True)
        old_columns = self.mrr.columns
        new_columns = pd.to_datetime(self.mrr.columns).strftime('%m/%Y')
        column_rename = {old_columns[i]: new_columns[i] for i in range(len(old_columns))}
        self.mrr.columns = new_columns
        self.mrr.apply(filter_to_dec_list)
        self.mrr.drop(self.mrr.tail(1).index, inplace=True)
        self.cohorts = self.cohorts.copy()
        self.cohorts.set_index("Customer", inplace=True)
        self.cohorts.iloc[:, 1:-1] = self.cohorts.iloc[:, 1:-1].apply(filter_to_dec_list)
        self.cohorts = self.cohorts[self.cohorts['Cohort']!="N/A"]

        # Rename columns to cohort months, filter data, make negative values
        for year in self.income_stat.keys():
            self.income_stat[year] = self.income_stat[year].rename(columns=column_rename)
            self.balance_sh[year] = self.balance_sh[year].rename(columns=column_rename)
            self.cash_flow[year] = self.cash_flow[year].rename(columns=column_rename)
            new_curr_columns = list(filter(lambda x: x.split("/")[1]==year, new_columns))
            self.income_stat[year].loc[:, new_curr_columns] = self.income_stat[year].loc[:, new_curr_columns].apply(filter_to_dec_list)
            self.balance_sh[year].loc[:, new_curr_columns] = self.balance_sh[year].loc[:, new_curr_columns].apply(filter_to_dec_list)
            self.cash_flow[year].loc[:, new_curr_columns] = self.cash_flow[year].loc[:, new_curr_columns].apply(filter_to_dec_list)

    def clean_outputs(self):
        self.base_build = self.base_build.astype(object)
        self.base_build.apply(nan_to_blank_list)
        base_build_copy = self.base_build.copy()
        self.base_build = self.base_build.apply(numbers_with_commas_list)
        self.base_build.loc['Churn %'] = base_build_copy.loc['Churn %'].apply(dec_to_percents)
        self.base_build.reset_index(inplace=True)

        self.rev_build = self.rev_build.astype(object)
        self.rev_build.apply(nan_to_blank_list)
        rev_build_copy = self.rev_build.copy()
        self.rev_build = self.rev_build.apply(zero_to_blank_list)
        self.rev_build = self.rev_build.apply(numbers_with_commas_list)
        self.rev_build.loc['Gross Churn %'] = rev_build_copy.loc['Gross Churn %'].apply(dec_to_percents)
        self.rev_build.loc['Upsell %'] = rev_build_copy.loc['Upsell %'].apply(dec_to_percents)
        self.rev_build.loc['New customer %'] = rev_build_copy.loc['New customer %'].apply(dec_to_percents)
        self.rev_build.reset_index(inplace=True)

        self.fin_perf = self.fin_perf.astype(object)
        self.fin_perf.apply(nan_to_blank_list)
        self.fin_perf_raw = self.fin_perf.copy()
        self.fin_perf = self.fin_perf.apply(numbers_with_commas_list)
        self.fin_perf.reset_index(inplace=True)
        self.fin_perf_raw.reset_index(inplace=True)

        self.oper_stats = self.oper_stats.astype(object)
        self.oper_stats.apply(nan_to_blank_list)
        self.oper_stats_raw = self.oper_stats.copy()
        self.oper_stats = self.oper_stats.apply(dec_to_percents_list)
        self.oper_stats.reset_index(inplace=True)
        self.oper_stats_raw.reset_index(inplace=True)

        self.oper_metrics = self.oper_metrics.astype(object)
        self.oper_metrics.apply(nan_to_blank_list)
        oper_metrics_copy = self.oper_metrics.copy()
        self.oper_metrics = self.oper_metrics.apply(zero_to_blank_list)
        self.oper_metrics = self.oper_metrics.apply(numbers_with_commas_list)
        self.oper_metrics.loc[['B', 'A', 'S', 'E']] = oper_metrics_copy.loc[['B', 'A', 'S', 'E']]
        self.oper_metrics.loc['Churn %'] = oper_metrics_copy.loc['Churn %'].apply(dec_to_percents)
        self.oper_metrics.loc['Net Churn %'] = oper_metrics_copy.loc['Net Churn %'].apply(dec_to_percents)
        self.oper_metrics.loc['Gross Churn %'] = oper_metrics_copy.loc['Gross Churn %'].apply(dec_to_percents)
        self.oper_metrics.loc['Upsell %'] = oper_metrics_copy.loc['Upsell %'].apply(dec_to_percents)
        self.oper_metrics.loc['New customer %'] = oper_metrics_copy.loc['New customer %'].apply(dec_to_percents)
        self.oper_metrics.reset_index(inplace=True)

        self.bal_sheet = self.bal_sheet.astype(object)
        self.bal_sheet.apply(nan_to_blank_list)
        self.bal_sheet.apply(zero_to_blank_list)
        self.bal_sheet = self.bal_sheet.apply(numbers_with_commas_list)
        self.bal_sheet.reset_index(inplace=True)

        self.cash_flow_stat = self.cash_flow_stat.astype(object)
        self.cash_flow_stat.apply(nan_to_blank_list)
        self.cash_flow_stat.apply(zero_to_blank_list)
        self.cash_flow_stat = self.cash_flow_stat.apply(numbers_with_commas_list)
        self.cash_flow_stat.reset_index(inplace=True)

        self.oth_metrics = self.oth_metrics.astype(object)
        self.oth_metrics.apply(nan_to_blank_list)
        oth_metrics_copy = self.oth_metrics.copy()
        self.oth_metrics = self.oth_metrics.apply(numbers_with_commas_list)
        self.oth_metrics.loc['FCF margin'] = oth_metrics_copy.loc['FCF margin'].apply(dec_to_percents)
        self.oth_metrics.loc['ARR Growth'] = oth_metrics_copy.loc['ARR Growth'].apply(dec_to_percents)
        self.oth_metrics.loc['Efficiency Score'] = oth_metrics_copy.loc['Efficiency Score'].apply(dec_to_percents)
        self.oth_metrics.loc['Ratio'] = oth_metrics_copy.loc['Ratio'].apply(dec_to_tenths)
        self.oth_metrics.loc['Ratio*'] = oth_metrics_copy.loc['Ratio*'].apply(dec_to_tenths)
        self.oth_metrics.loc['TTM Ratio'] = oth_metrics_copy.loc['TTM Ratio'].apply(dec_to_tenths)
        self.oth_metrics.loc['TTM Ratio*'] = oth_metrics_copy.loc['TTM Ratio*'].apply(dec_to_tenths)
        self.oth_metrics.loc['Quick Ratio'] = oth_metrics_copy.loc['Quick Ratio'].apply(dec_to_tenths)
        self.oth_metrics.reset_index(inplace=True)

        print("BASE Build Support")
        print(self.base_build)
        print("Rev Build Support")
        print(self.rev_build)
        print("Financial Performance")
        print(self.fin_perf)
        print("Operating Statistics")
        print(self.oper_stats)
        print("Operating Metrics")
        print(self.oper_metrics)
        print("Balance Sheet")
        print(self.bal_sheet)
        print("Cash Flow Statement")
        print(self.cash_flow_stat)
        print("Other Metrics")
        print(self.oth_metrics)

    def base_build_support(self):
        # Create intermediate table for calculating BASE
        self.base_interm = self.mrr.iloc[:-1].copy()
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
        self.base_build.loc['B'] = [float("NaN")] + list(self.base_build.loc['E'].iloc[:-1])
        a = []
        for i in range(1, self.base_build.shape[1]):
            a.append(len(self.base_interm[(self.base_interm.iloc[:, i-1] == 0) & (self.base_interm.iloc[:, i] == 1)]))
        self.base_build.loc['A'] = [float("NaN")] + a
        self.base_build.loc['S'] = [float("NaN")] + list(self.base_build.loc['E'].iloc[1:]-self.base_build.loc['B'].iloc[1:]-self.base_build.loc['A'].iloc[1:])
        self.base_build.loc['Churn %'] = [float("NaN")] + list(self.base_build.loc['S'].iloc[1:]/self.base_build.loc['B'].iloc[1:].replace({0:np.nan}))

    def rev_build_support(self):
        # Calculate upsell formulas
        self.upsell = self.mrr.iloc[:-1].copy()
        self.upsell = self.upsell.apply(lambda x: pd.Series([0]+[max(0, min(x[i]-x[i-1], x[i], x[i-1])) for i in range(1, x.shape[0])], self.upsell.columns), axis=1)

        # Calculate decrease MRR formulas
        self.decrease_mrr = self.mrr.iloc[:-1].copy()
        self.decrease_mrr.columns = pd.to_datetime(self.decrease_mrr.columns).strftime('%m/%Y')
        self.decrease_mrr = self.decrease_mrr.apply(lambda x: pd.Series([0]+[max(float('-inf'), min(x[i]-x[i-1], x[i], x[i-1], 0)) for i in range(1, x.shape[0])], self.decrease_mrr.columns), axis=1)

        # Calculate final Total MRR table
        total_mrr_index = ["Beginning MRR", "Lost customers", "Decrease", "Increase", "New customers", "Ending MRR", "Total Additions", "Total Subtractions", "Gross Churn %", "Upsell %", "New customer %"]
        self.rev_build = pd.DataFrame(index=np.arange(len(total_mrr_index)), columns=self.upsell.columns)
        self.rev_build.set_index(pd.Series(total_mrr_index, name='Total MRR'), inplace=True)
        self.rev_build.loc['Ending MRR'] = list(self.mrr.loc['Grand Total'])
        self.rev_build.loc['Beginning MRR'] = [float("NaN")] + list(self.rev_build.loc['Ending MRR'].iloc[:-1])
        l, n = [], []
        for i in range(1, self.mrr.shape[1]):
            l.append(-sum(self.mrr[(self.mrr.iloc[:, i-1] != 0) & (self.mrr.iloc[:, i] == 0)].iloc[:, i-1]))
            n.append(sum(self.mrr[(self.mrr.iloc[:, i-1] == 0) & (self.mrr.iloc[:, i] != 0)].iloc[:, i]))
        self.rev_build.loc['Lost customers'] = [float("NaN")] + l
        self.rev_build.loc['New customers'] = [float("NaN")] + n
        self.rev_build.loc['Decrease'] = [float("NaN")] + list(self.decrease_mrr.iloc[:, 1:].sum())
        self.rev_build.loc['Increase'] = [float("NaN")] + list(self.upsell.iloc[:, 1:].sum())

        self.rev_build.loc['Total Additions'] = [float("NaN")] + list(self.rev_build.loc['Increase'].iloc[1:]+self.rev_build.loc['New customers'].iloc[1:])
        self.rev_build.loc['Total Subtractions'] = [float("NaN")] + list(self.rev_build.loc['Decrease'].iloc[1:]+self.rev_build.loc['Lost customers'].iloc[1:])

        self.rev_build.loc['Gross Churn %'] = [float("NaN")] + list(self.rev_build.loc['Total Subtractions'].iloc[1:]/self.rev_build.loc['Beginning MRR'].iloc[1:].replace({0:np.nan}))
        self.rev_build.loc['Upsell %'] = [float("NaN")] + list(self.rev_build.loc['Increase'].iloc[1:]/self.rev_build.loc['Beginning MRR'].iloc[1:].replace({0:np.nan}))
        self.rev_build.loc['New customer %'] = [float("NaN")] + list(self.rev_build.loc['New customers'].iloc[1:]/self.rev_build.loc['Ending MRR'].iloc[1:].replace({0:np.nan}))

    def label_helper(self, labels_dict, data, label):
        old_label = labels_dict[label][1]
        sheet_source = labels_dict[label][0]
        values = [sheet_source[col.split("/")[1]][sheet_source[col.split("/")[1]]['Labels']==old_label].loc[:, col].sum()/1000 for col in data.columns]
        data.loc[label] = [-value for value in values] if label in ["COGS", "Recurring Revenue COGS", "Professional Services COGS", "R&D", "S&M", "Customer Success", "G&A", "Uncategorized Expense", "D&A", "Interest Expense"] else values

    def financial_performance(self):
        index = ["ARR", "Revenue", "Recurring Revenue", "Non-Recurring Revenue", "Professional Services", "COGS", "Recurring Revenue COGS", "Professional Services COGS", "Gross Profit", "Expenses", "R&D", "S&M", "Customer Success", "G&A", "EBITDA", "Uncategorized Expense", "D&A", "Interest Expense", "Net Other Income", "Net Income"]
        self.fin_perf = pd.DataFrame(index=np.arange(len(index)), columns=self.mrr.columns)
        self.fin_perf.set_index(pd.Series(index, name='Financial Performance'), inplace=True)
        fin_perf_dict = {
            "Recurring Revenue": [self.income_stat, "Recurring Revenue"],
            "Non-Recurring Revenue": [self.income_stat, "Non-Recurring Revenue"],
            "Professional Services": [self.income_stat, "Professional Services"],
            "COGS": [self.income_stat, "COGS"],
            "Recurring Revenue COGS": [self.income_stat, "Recurring Revenue COGS"],
            "Professional Services COGS": [self.income_stat, "Professional Services COGS"],
            "R&D": [self.income_stat, "R&D"],
            "S&M": [self.income_stat, "S&M"],
            "Customer Success": [self.income_stat, "Customer Success"],
            "G&A": [self.income_stat, "G&A"],
            "Uncategorized Expense": [self.income_stat, "Uncategorized Expense"],
            "D&A": [self.income_stat, "D&A"],
            "Interest Expense": [self.income_stat, "Interest Expense"],
            "Net Other Income": [self.income_stat, "Net Other Income"],
        }
        for label in fin_perf_dict.keys():
            self.label_helper(fin_perf_dict, self.fin_perf, label)

        self.fin_perf.loc['ARR'] = list(self.oper_metrics.loc['Ending ARR']/1000)
        self.fin_perf.loc['Revenue'] = list(self.fin_perf.loc[['Recurring Revenue', 'Non-Recurring Revenue', 'Professional Services']].sum())
        self.fin_perf.loc['COGS'] = list(self.fin_perf.loc[['COGS', 'Recurring Revenue COGS', 'Professional Services COGS']].sum())
        self.fin_perf.loc['Gross Profit'] = list(self.fin_perf.loc[['Revenue', 'COGS']].sum())
        self.fin_perf.loc['Expenses'] = list(self.fin_perf.loc[['R&D', 'S&M', 'Customer Success', 'G&A']].sum())
        self.fin_perf.loc['EBITDA'] = list(self.fin_perf.loc[['Gross Profit', 'Expenses']].sum())
        self.fin_perf.loc['Net Income'] = list(self.fin_perf.loc[['EBITDA', 'Uncategorized Expense', 'D&A', 'Interest Expense', 'Net Other Income']].sum())

    def operating_statistics(self):
        index = ["Growth", "ARR YoY", "Revenue YoY", "Recurring Revenue YoY", "Professional Services YoY", "Revenue Period over Period", "Gross Margin", "Recurring Revenue Gross Margin", "Professional Services Gross Margin", "Contribution Margin", "Recurring Revenue Contribution Margin", "% of Sales", "Expenses", "R&D", "S&M", "G&A", "EBITDA Margin"]
        self.oper_stats = pd.DataFrame(index=np.arange(len(index)), columns=self.mrr.columns)
        self.oper_stats.set_index(pd.Series(index, name='Operating Statistics'), inplace=True)
        self.oper_stats.loc['ARR YoY'] = ["N/A"]*12 + list(self.fin_perf.loc['ARR'].iloc[12:].array/self.fin_perf.loc['ARR'].iloc[:-12].replace({0:np.nan}).array-1)
        self.oper_stats.loc['Revenue YoY'] = ["N/A"]*12 + list(self.fin_perf.loc['Revenue'].iloc[12:].array/self.fin_perf.loc['Revenue'].iloc[:-12].replace({0:np.nan}).array-1)
        self.oper_stats.loc['Recurring Revenue YoY'] = ["N/A"]*12 + list(self.fin_perf.loc['Recurring Revenue'].iloc[12:].array/self.fin_perf.loc['Recurring Revenue'].iloc[:-12].replace({0:np.nan}).array-1)
        self.oper_stats.loc['Professional Services YoY'] = ["N/A"]*12 + list(self.fin_perf.loc['Professional Services'].iloc[12:].array/self.fin_perf.loc['Professional Services'].iloc[:-12].replace({0:np.nan}).array-1)
        self.oper_stats.loc['Revenue Period over Period'] = ["N/A"] + list(self.fin_perf.loc['Revenue'].iloc[1:].array/self.fin_perf.loc['Revenue'].iloc[:-1].replace({0:np.nan}).array-1)
        self.oper_stats.loc['Gross Margin'] = self.fin_perf.loc['Gross Profit'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan}))
        self.oper_stats.loc['Recurring Revenue Gross Margin'] = list((self.fin_perf.loc['Recurring Revenue']+self.fin_perf.loc['Recurring Revenue COGS'])/self.fin_perf.loc['Recurring Revenue'].replace({0:np.nan}))
        self.oper_stats.loc['Professional Services Gross Margin'] = list((self.fin_perf.loc['Professional Services']+self.fin_perf.loc['Professional Services COGS'])/self.fin_perf.loc['Professional Services'].replace({0:np.nan}))
        self.oper_stats.loc['Contribution Margin'] = self.oper_stats.loc['Gross Margin']
        self.oper_stats.loc['Recurring Revenue Contribution Margin'] = self.oper_stats.loc['Recurring Revenue Gross Margin']
        self.oper_stats.loc['Expenses'] = self.fin_perf.loc['Expenses'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan}))
        self.oper_stats.loc['R&D'] = self.fin_perf.loc['R&D'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan}))
        self.oper_stats.loc['S&M'] = self.fin_perf.loc['S&M'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan}))
        self.oper_stats.loc['G&A'] = self.fin_perf.loc['G&A'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan}))
        self.oper_stats.loc['EBITDA Margin'] = self.fin_perf.loc['EBITDA'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan}))

    def operating_metrics(self):
        base_index = ["B", "A", "S", "E", "Churn %"]
        rev_index = ["Beginning MRR", "Lost customers", "Decrease", "Increase", "New customers", "Ending MRR", "Total Additions", "Total Subtractions", "Gross Churn %", "Upsell %", "New customer %"]
        index = ["Customer Build"] + base_index + ["MRR Build"] + rev_index[:6] + ["Ending ARR"] + rev_index[6:-3] + ["Net Churn %"] + rev_index[-3:]
        self.oper_metrics = pd.DataFrame(index=np.arange(len(index)), columns=self.mrr.columns)
        self.oper_metrics.set_index(pd.Series(index, name='Operating Metrics'), inplace=True)
        self.oper_metrics.loc[base_index] = self.base_build.loc[base_index]
        self.oper_metrics.loc[rev_index] = self.rev_build.loc[rev_index]
        self.oper_metrics.loc['Ending ARR'] = self.oper_metrics.loc['Ending MRR']*12
        self.oper_metrics.loc['Net Churn %'] = list((self.oper_metrics.loc['Total Subtractions']+self.oper_metrics.loc['Increase'])/self.oper_metrics.loc['Beginning MRR'].replace({0:np.nan}))

    def balance_sheet(self):
        index = ["ASSETS", "Current Assets", "Cash", "AR", "Other Current Assets", "Total Current Assets", "Fixed Assets", "Other Non-Current Assets", "Total Non-Current Assets", "TOTAL ASSETS", "LIABILITIES", "Current Liabilities", "AP", "Deferred Revenue", "Other Current Liabilities", "Total Current Liabilities", "Loans Payable", "Long-Term Liabilities", "TOTAL LIABILITIES", "EQUITY", "Common Stock", "Distributions", "Retained Earnings", "Preferred Stock", "Accumulated Other Comprehensive Income", "Total Equity", "TOTAL LIABILITIES & EQUITY"]
        self.bal_sheet = pd.DataFrame(index=np.arange(len(index)), columns=self.mrr.columns)
        self.bal_sheet.set_index(pd.Series(index, name='Balance Sheet'), inplace=True)
        bal_sheet_dict = {
            "Cash": [self.balance_sh, "Cash"],
            "AR": [self.balance_sh, "AR"],
            "Other Current Assets": [self.balance_sh, "Other Current Assets"],
            "Fixed Assets": [self.balance_sh, "Fixed Assets"],
            "Other Non-Current Assets": [self.balance_sh, "Other Non-Current Assets"],
            "AP": [self.balance_sh, "AP"],
            "Deferred Revenue": [self.balance_sh, "Deferred Revenue"],
            "Other Current Liabilities": [self.balance_sh, "Other Current Liabilities"],
            "Loans Payable": [self.balance_sh, "Loans Payable"],
            "Long-Term Liabilities": [self.balance_sh, "Long-Term Liabilities"],
            "Common Stock": [self.balance_sh, "Common Stock"],
            "Distributions": [self.balance_sh, "Distributions"],
            "Retained Earnings": [self.balance_sh, "Retained Earnings"],
            "Preferred Stock": [self.balance_sh, "Preferred Stock"],
            "Accumulated Other Comprehensive Income": [self.balance_sh, "Accumulated Other Comprehensive Income"],
            "Total Equity": [self.balance_sh, "Total Equity"],
        }
        for label in bal_sheet_dict.keys():
            self.label_helper(bal_sheet_dict, self.bal_sheet, label)

        self.bal_sheet.loc['Total Current Assets'] = list(self.bal_sheet.loc[['Cash', 'AR', 'Other Current Assets']].sum())
        self.bal_sheet.loc['Total Non-Current Assets'] = list(self.bal_sheet.loc[['Fixed Assets', 'Other Non-Current Assets']].sum())
        self.bal_sheet.loc['TOTAL ASSETS'] = list(self.bal_sheet.loc[['Total Current Assets', 'Total Non-Current Assets']].sum())
        self.bal_sheet.loc['Total Current Liabilities'] = list(self.bal_sheet.loc[['AP', 'Deferred Revenue', 'Other Current Liabilities']].sum())
        self.bal_sheet.loc['Long-Term Liabilities'] = list(self.bal_sheet.loc[['Long-Term Liabilities', 'Loans Payable']].sum())
        self.bal_sheet.loc['TOTAL LIABILITIES'] = list(self.bal_sheet.loc[['Total Current Liabilities', 'Long-Term Liabilities']].sum())
        self.bal_sheet.loc['Total Equity'] = list(self.bal_sheet.loc[['Total Equity', 'Common Stock', 'Distributions', 'Retained Earnings', 'Preferred Stock', 'Accumulated Other Comprehensive Income']].sum())
        self.bal_sheet.loc['TOTAL LIABILITIES & EQUITY'] = list(self.bal_sheet.loc[['TOTAL LIABILITIES', 'Total Equity']].sum())

    def cash_flow_statement(self):
        index = ["CFO", "CFI", "CFF", "Increase (Decrease) in Cash", "Cash at beginning of period", "Cash at end of period", "Free Cash Flow"]
        self.cash_flow_stat = pd.DataFrame(index=np.arange(len(index)), columns=self.mrr.columns)
        self.cash_flow_stat.set_index(pd.Series(index, name='Cash Flow Statement'), inplace=True)
        cash_flow_stat_dict = {
            "CFO": [self.cash_flow, "Net cash provided by operating activities"],
            "CFI": [self.cash_flow, "Net cash provided by investing activities"],
            "CFF": [self.cash_flow, "Net cash provided by financing activities"],
        }
        for label in cash_flow_stat_dict.keys():
            self.label_helper(cash_flow_stat_dict, self.cash_flow_stat, label)

        self.cash_flow_stat.loc['Increase (Decrease) in Cash'] = list(self.cash_flow_stat.loc[['CFO', 'CFI', 'CFF']].sum())
        self.cash_flow_stat.loc['Cash at end of period'][0] = self.bal_sheet.loc['Cash'][0]
        for i in range(1, self.cash_flow_stat.shape[1]):
            self.cash_flow_stat.loc['Cash at end of period'][i] = self.cash_flow_stat.loc['Cash at end of period'][i-1] + self.cash_flow_stat.loc['Increase (Decrease) in Cash'][i]
        self.cash_flow_stat.loc['Cash at beginning of period'] = [float("NaN")] + list(self.cash_flow_stat.loc['Cash at end of period'].iloc[:-1])
        self.cash_flow_stat.loc['Free Cash Flow'] = list(self.cash_flow_stat.loc[['CFO', 'CFI']].sum())

    def other_metrics(self):
        index = ["ARR", "Net New ARR", "EBITDA", "Ratio", "TTM Ratio", "Net New ARR*", "FCF", "Ratio*", "TTM Ratio*", "FCF*", "FCF margin", "ARR Growth", "Efficiency Score", "Avg ARR per Customer", "Total Additions", "Total Subtractions", "Quick Ratio"]
        self.oth_metrics = pd.DataFrame(index=np.arange(len(index)), columns=self.mrr.columns)
        self.oth_metrics.set_index(pd.Series(index, name='Other Metrics'), inplace=True)
        self.oth_metrics.loc['ARR'] = self.oper_metrics.loc['Ending ARR']
        self.oth_metrics.loc['Net New ARR'] = [float("NaN")] + list(self.oth_metrics.loc['ARR'].iloc[1:].array-self.oth_metrics.loc['ARR'].iloc[:-1].array)
        self.oth_metrics.loc['EBITDA'] = [float("NaN")] + list(self.fin_perf.loc['EBITDA'].iloc[1:]*1000)
        self.oth_metrics.loc['Ratio'] = self.oth_metrics.loc['Net New ARR'].div(-self.oth_metrics.loc['EBITDA'].replace({0:np.nan}))
        self.oth_metrics.loc['Net New ARR*'] = self.oth_metrics.loc['Net New ARR']
        self.oth_metrics.loc['FCF'] = [float("NaN")] + list(self.cash_flow_stat.loc[['CFO', 'CFI']].iloc[:, 1:].sum()*1000)
        self.oth_metrics.loc['Ratio*'] = self.oth_metrics.loc['Net New ARR*'].div(-self.oth_metrics.loc['FCF'].replace({0:np.nan}))
        self.oth_metrics.loc['FCF*'] = self.oth_metrics.loc['FCF']
        self.oth_metrics.loc['TTM Ratio'][:12] = [float("NaN")]*12
        self.oth_metrics.loc['TTM Ratio*'][:12] = [float("NaN")]*12
        for i in range(12, self.oth_metrics.shape[1]):
            self.oth_metrics.loc['TTM Ratio'][i] = -self.oth_metrics.loc['Net New ARR'].iloc[i-11:i+1].sum()/(self.oth_metrics.loc['EBITDA'].iloc[i-11:i+1].sum() if self.oth_metrics.loc['EBITDA'].iloc[i-11:i+1].sum() != 0 else float("NaN"))
            self.oth_metrics.loc['TTM Ratio*'][i] = -self.oth_metrics.loc['Net New ARR*'].iloc[i-11:i+1].sum()/(self.oth_metrics.loc['FCF'].iloc[i-11:i+1].sum() if self.oth_metrics.loc['FCF'].iloc[i-11:i+1].sum() != 0 else float("NaN"))
        self.oth_metrics.loc['FCF margin'] = self.oth_metrics.loc['FCF'].div(self.fin_perf.loc['Revenue'].replace({0:np.nan})*1000)
        self.oth_metrics.loc['ARR Growth'] = [float("NaN")] + list(self.oper_stats.loc['ARR YoY'][1:])
        self.oth_metrics.loc['Efficiency Score'] = [float("NaN")] + ["N/A"]*11 + list(self.oth_metrics.loc[['FCF margin', 'ARR Growth']].iloc[:, 12:].sum())
        self.oth_metrics.loc['Avg ARR per Customer'] = self.oper_metrics.loc['Ending ARR'].div(self.oper_metrics.loc['E'].replace({0:np.nan}))
        self.oth_metrics.loc[['Total Additions', 'Total Subtractions']] = self.oper_metrics.loc[['Total Additions', 'Total Subtractions']]
        self.oth_metrics.loc['Quick Ratio'] = self.oth_metrics.loc['Total Additions'].div(-self.oth_metrics.loc['Total Subtractions'].replace({0:np.nan}))
