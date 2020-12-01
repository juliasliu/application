'''Python script to generate cohort analysis spreadsheets based on SEMrush inputs'''
'''Authors - @Julia Liu
'''

import numpy as np
import pandas as pd
from datetime import datetime

class CohortAnalysis:

    def __init__(self, csv):
        self.csv_path = 'inputs/' + csv
        # Determine file path to append to output csv files
        period = csv.split("_")[-2]
        self.file_path = 'outputs/semrush_' + period + '_'


    def clean_inputs(self):
        apr = pd.read_csv(self.csv_path)
        self.apr_sorted = apr.sort_values('reg_date')
        # print("ORIGINAL INPUT FILE")
        # print(self.apr_sorted)

        # Create a period column based on the reg_date column
        self.apr_sorted['reg_date'] = pd.to_datetime(self.apr_sorted['reg_date'])
        self.apr_sorted['reg_date_period'] = self.apr_sorted.reg_date.apply(lambda x: x.strftime('%Y-%m'))

        # Create a period column based on the first payment column
        self.apr_sorted['first_payment'] = self.apr_sorted.iloc[:, 2:].keys()[np.argmax(self.apr_sorted.iloc[:, 2:].values!=0.0,axis=1)]
        self.apr_sorted['first_payment'] = pd.to_datetime(self.apr_sorted['first_payment'])
        self.apr_sorted['first_payment_period'] = self.apr_sorted.first_payment.apply(lambda x: x.strftime('%Y-%m'))
        # print("AGGREGATED INPUTS")
        # print(self.apr_sorted)

        # If customer made a first payment before their registration date, change their registration date bucket
        self.apr_sorted['reg_date_modified'] = self.apr_sorted.apply(lambda x: min(x.reg_date, x.first_payment), axis=1)
        self.apr_sorted['reg_date_period_modified'] = self.apr_sorted.reg_date_modified.apply(lambda x: x.strftime('%Y-%m'))
        # print("MODIFIED BUCKETS FOR AGGREGATED INPUTS")
        # print(self.apr_sorted)

    def revenue_cohorts_first_payment(self):
        # 1. REVENUE COHORTS - DATE OF FIRST PAYMENT
        revenue_cohorts = self.apr_sorted.groupby(by=['first_payment_period'], as_index=False).sum()
        revenue_cohorts_final = revenue_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        revenue_cohorts_final.set_axis(revenue_cohorts.columns[revenue_cohorts_final.columns], axis=1, inplace=False)
        # print("REVENUE COHORTS FINAL")
        # print(revenue_cohorts_final)
        revenue_cohorts_final.to_csv(r'' + self.file_path + 'revenue.csv', index=False)

    def customer_cohorts_first_payment(self):
        # 2. CUSTOMER COHORTS - DATE OF FIRST PAYMENT
        customer_cohorts = self.apr_sorted.drop(["id_smart", "reg_date", "reg_date_period", "first_payment", "reg_date_modified", "reg_date_period_modified"], axis=1)
        customer_cohorts = customer_cohorts.groupby(by=['first_payment_period'], as_index=False).agg(lambda x: x.ne(0).sum())
        customer_cohorts_final = customer_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        customer_cohorts_final.set_axis(customer_cohorts.columns[customer_cohorts_final.columns], axis=1, inplace=False)
        # print("CUSTOMER COHORTS FINAL")
        # print(customer_cohorts_final)
        customer_cohorts_final.to_csv(r'' + self.file_path + 'customer.csv', index=False)

    def revenue_cohorts_registration_date(self):
        # 3. REVENUE COHORTS - REGISTRATION DATE
        reg_revenue_cohorts = self.apr_sorted.groupby(by=['reg_date_period_modified'], as_index=False).sum()
        reg_revenue_cohorts_final = reg_revenue_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        reg_revenue_cohorts_final.set_axis(reg_revenue_cohorts.columns[reg_revenue_cohorts_final.columns], axis=1, inplace=False)
        # print("REGISTRATION REVENUE COHORTS FINAL")
        # print(reg_revenue_cohorts_final)
        reg_revenue_cohorts_final.to_csv(r'' + self.file_path + 'reg_revenue.csv', index=False)

    def customer_cohorts_registration_date(self):
        # 4. CUSTOMER COHORTS - REGISTRATION DATE
        reg_customer_cohorts = self.apr_sorted.drop(["id_smart", "reg_date", "reg_date_period", "first_payment", "first_payment_period", "reg_date_modified"], axis=1)
        reg_customer_cohorts = reg_customer_cohorts.groupby(by=['reg_date_period_modified'], as_index=False).agg(lambda x: x.ne(0).sum())
        reg_customer_cohorts_final = reg_customer_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        reg_customer_cohorts_final.set_axis(reg_customer_cohorts.columns[reg_customer_cohorts_final.columns], axis=1, inplace=False)
        # print("REGISTRATION CUSTOMER COHORTS FINAL")
        # print(reg_customer_cohorts_final)
        reg_customer_cohorts_final.to_csv(r'' + self.file_path + 'reg_customer.csv', index=False)

    def customer_cohorts_register_pay_m1(self):
        # 5. CUSTOMER COHORTS - REGISTER AND PAY IN M1
        m1_customer_cohorts = self.apr_sorted.drop(["id_smart", "reg_date", "reg_date_period_modified", "first_payment", "reg_date_modified"], axis=1)
        # Only keep the customers who have registered and paid in the same month
        m1_customer_cohorts = m1_customer_cohorts[m1_customer_cohorts["reg_date_period"] == m1_customer_cohorts["first_payment_period"]]
        m1_customer_cohorts = m1_customer_cohorts.drop(["first_payment_period"], axis=1)
        m1_customer_cohorts = m1_customer_cohorts.groupby(by=['reg_date_period'], as_index=False).agg(lambda x: x.ne(0).sum())
        m1_customer_cohorts_final = m1_customer_cohorts.apply(lambda x: pd.Series(x[x != 0].dropna().values), axis=1)
        m1_customer_cohorts_final.set_axis(m1_customer_cohorts.columns[m1_customer_cohorts_final.columns], axis=1, inplace=False)
        # print("REGISTRATION CUSTOMER COHORTS FINAL")
        # print(m1_customer_cohorts_final)
        m1_customer_cohorts_final.to_csv(r'' + self.file_path + 'm1_customer.csv', index=False)


'''Main Method': takes in specified file path and runs analysis'''
if __name__ == "__main__":
	file_path = input("Paste name of the input csv file: ")

	c = CohortAnalysis(file_path)

	print('Cleaning input data...')
	c.clean_inputs()
	print(' -- DONE -- ')

	print('Running revenue cohorts - date of first payment...')
	c.revenue_cohorts_first_payment()
	print(' -- DONE -- ')

	print('Running customer cohorts - date of first payment...')
	c.customer_cohorts_first_payment()
	print(' -- DONE -- ')

	print('Running revenue cohorts - registration date...')
	c.revenue_cohorts_registration_date()
	print(' -- DONE -- ')

	print('Running customer cohorts - registration date...')
	c.customer_cohorts_registration_date()
	print(' -- DONE -- ')

	print('Running customer cohorts - register and pay in M1...')
	c.customer_cohorts_register_pay_m1()
	print(' -- DONE -- ')

	print('Files located under outputs/ folder.')
