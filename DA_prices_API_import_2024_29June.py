#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:59:45 2024
@author: mayk
"""
#%% import packages
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
import datetime
from entsoe import EntsoeRawClient
from entsoe import EntsoePandasClient

#%% set API key, date, location
client = EntsoePandasClient(api_key="4a2ed80d-d974-47ef-8d11-778e05f67850")
start   = pd.Timestamp('20240101T00', tz='Europe/Brussels')
end     = pd.Timestamp('20240108T00', tz='Europe/Brussels') # '20230101T23'
country_code = 'NL'  # Netherlands, #country_code_from = 'FR'  # France, #country_code_to = 'DE_LU' # Germany-Luxembourg
# type_marketagreement_type = 'A01'
# contract_marketagreement_type = "A01"

#%% Run retrieval Query for Day-Ahead and Imbalance prices both
DA  = client.query_day_ahead_prices(country_code, start=start, end=end)
imb = client.query_imbalance_prices(country_code, start=start,end=end, psr_type=None)
imb = imb.drop('Short', axis=1) # axis = 1 means columns, axis = 0 means delete row from df.

#%% Export dataframes to .xlsx or .csv
DA.to_excel('outfile_DA_2024_test.xlsx', index=False)
imb.to_excel('outfile_imb_2024_test.xlsx', index=False)
#DA.to_csv('outfile_DA_2024_Jan_22Apr.csv', header=['DA_price'])
#imb.to_csv('outfile_imb_2024_Jan_22Apr.csv', header=['imb_price'])

#%% DA prices to 15min values by duplicating




#%% Plot data






