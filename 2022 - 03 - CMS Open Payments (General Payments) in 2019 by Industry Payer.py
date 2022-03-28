#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Date: 2022-03-27
Filename: 2022 - 03 - CMS Open Payments (General Payments) in 2019 by Industry Payer.py
Author: Megan McCabe
Script Purpose:    
    Generate a plot demonstrating the count of payments and sum of payments 
made by industry payers in 2019 to covered CMS (Center for Medicare and Medicaid) recipients, 
including physicians and teaching hospitals. The general payments dataset is 8Gb, so the script 
leverages chunking to pull a subset of columns for this quick visualization exercise. 
CMS Open Payments seeks to make industry payments to healthcare institutions and providers more transparent. 
More information about the Open Payments program is available here: https://www.cms.gov/openpayments.
    
    
Note: I should have used 'payer' in the place of 'payor' for the variable names
below. The term 'payer' indicates 'maker of a payment' whereas 'payor' indicates
'healthcare insurance'. In this project, the manufacturer or group purchasing
organization (GPO) would be most appropriately characterized as the 'payer'.
'''

# 0. Accronyms:
    # gp = general payments
    # phys = physician
    
    
# 1. Import packages

import pandas as pd
import matplotlib.pyplot as plt

# 2. Load gen payments data (in chunks due to large file size -- 6Gb & laptop has 8Gb RAM)

data_filepath = '/Users/megan_mccabe/documents/data_science/2021 - CMS Open Payments Project/data/'
gp_filename = 'OP_DTL_GNRL_PGYR2019_P06302021.csv'


def subset_gp_df(chunk):
    return chunk[['Record_ID',
                  'Physician_Profile_ID', 
                 'Physician_Specialty', 
                 'Recipient_Zip_Code',
                 'Recipient_State',
                 'Submitting_Applicable_Manufacturer_or_Applicable_GPO_Name', 
                 'Total_Amount_of_Payment_USDollars', 
                 'Date_of_Payment']]

gp_chunks = pd.read_csv(data_filepath+gp_filename,iterator=True,
                        chunksize=1000000,low_memory=False,parse_dates=['Date_of_Payment'])
gp_subsetted_chunks = map(subset_gp_df,gp_chunks)
gp_df = pd.concat(gp_subsetted_chunks,ignore_index=True)

# 3. Rename the raw data columns to be easier to work with

gp_col_map = {'Record_ID':'record_id',
              'Physician_Profile_ID':'phys_id', 
             'Physician_Specialty':'phys_specialty', 
             'Recipient_Zip_Code':'phys_zip',
             'Recipient_State':'phys_state',
             'Submitting_Applicable_Manufacturer_or_Applicable_GPO_Name':'payor', 
             'Total_Amount_of_Payment_USDollars':'payment_amt', 
             'Date_of_Payment':'date'}
gp_df.rename(mapper=gp_col_map,inplace=True,axis='columns')

# 4. Reformat data to look at payments by industry payor -- pt 1: First aggregation

gp_payor_desc = pd.pivot_table(gp_df,values=['record_id','payment_amt'],
                               aggfunc={'record_id':'count','payment_amt':'sum'},
                               index='payor')

gp_payor_desc.reset_index(inplace=True)
gp_top_10_payors = list(gp_payor_desc.sort_values(by='record_id',ascending=False)[:10].index)
gp_payor_desc.loc[gp_payor_desc['payor'].isin(gp_top_10_payors)==False,'payor'] = 'Other'

# 5. Reformat data to look at payments by industry payor -- pt 2: Isolating top 10 by payment counts

gp_payor_desc_2 = pd.pivot_table(gp_payor_desc,values=['record_id','payment_amt'],
                               aggfunc={'record_id':'sum','payment_amt':'sum'},
                               index='payor')

gp_payor_desc_2.drop(index='Other',inplace=True)
gp_payor_desc_2.reset_index(inplace=True)
gp_payor_desc_2.sort_values(by='record_id',ascending=False,inplace=True)
gp_payor_desc_2.reset_index(inplace=True)
gp_payor_desc_2.drop(columns='index',inplace=True)
gp_payor_desc_2['record_id'] = gp_payor_desc_2['record_id']/10**6
gp_payor_desc_2['payment_amt'] = gp_payor_desc_2['payment_amt']/10**6

# 6. Plot the payment counts & amount by payor

fig_gp_payor, ax_gp_payor1 = plt.subplots()

ax_gp_payor1.bar(gp_payor_desc_2.index-0.125,gp_payor_desc_2['record_id'],color='r',width=0.25)
ax_gp_payor1.set_xticks(range(10))
ax_gp_payor1.set_xticklabels(list(gp_payor_desc_2['payor']),rotation=90)
ax_gp_payor1.set_yticks(ax_gp_payor1.get_yticks())
ax_gp_payor1.set_yticklabels(['{:.1f}M'.format(x) for x in ax_gp_payor1.get_yticks()])
ax_gp_payor1.set_ylabel('Number of Payments')

ax_gp_payor2 = ax_gp_payor1.twinx()
ax_gp_payor2.bar(gp_payor_desc_2.index+0.125,gp_payor_desc_2['payment_amt'],color='b',width=0.25)
ax_gp_payor2.set_yticks(ax_gp_payor2.get_yticks())
ax_gp_payor2.set_yticklabels(['${:.0f}M'.format(x) for x in ax_gp_payor2.get_yticks()])
ax_gp_payor2.set_ylabel('Sum of Payments')
ax_gp_payor2.spines['right'].set_color('blue')

ax_gp_payor2.spines['left'].set_color('red')
ax_gp_payor2.spines[['right','left']].set_linewidth(2)
ax_gp_payor2.set_title('Open Payments Reported in 2019: By Industry Payer')

plt.show()






