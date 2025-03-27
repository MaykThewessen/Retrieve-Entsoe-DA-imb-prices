#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:59:45 2024
v6: Updated on Dec 2024
@author: Mayk Thewessen
"""

# Clear all variables
try:
    from IPython import get_ipython
    get_ipython().magic('reset -f')
except:
    pass

# Clear plots if matplotlib is used
try:
    import matplotlib.pyplot as plt
    plt.close('all')
except:
    pass

# Clear console (optional)
import os
os.system('clear')  # for Mac/Linux

#%% import packages
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
import datetime
from entsoe import EntsoeRawClient
from entsoe import EntsoePandasClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

#%% set API key, date, location
api_key = os.getenv('ENTSOE_API_KEY', 'default_api_key')
client = EntsoePandasClient(api_key=api_key)

print("Script started to retrieve Day-Ahead and Imbalance prices using Python and Entso-e API script")
start = pd.Timestamp('2024-01-01 00:00:00', tz='Europe/Brussels')
end   = pd.Timestamp('2025-01-01 00:00:00', tz='Europe/Brussels')
print(f"Start date: {start.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"End date:   {end.strftime('%Y-%m-%d %H:%M:%S')}")
country_code = 'NL'  # Netherlands, #country_code_from = 'FR'  # France, #country_code_to = 'DE_LU' # Germany-Luxembourg
# type_marketagreement_type = 'A01'
# contract_marketagreement_type = "A01"

#%%  Create datetime arrays first
datetime_hourly = pd.date_range(start=start, end=end, freq='h'    , tz='Europe/Brussels')  # Using 'h' instead of 'H'

# Print the first few entries to verify
print("\n datetime_hourly first rows:")
print(datetime_hourly[:5])
print("\n datetime_hourly last 5 rows:")
print(datetime_hourly[-5:])
print("\n")


datetime_15min  = pd.date_range(start=start, end=end, freq='15min', tz='Europe/Brussels')  # Using '15min' instead of '15T'

print(datetime_15min[:5])

#%% Retrieve and align price data

def get_da_prices_chunked(client, country_code, start, end):
    print("Starting to retrieve Day-Ahead prices in 90-day chunks:")
    # Create 90-day chunks
    chunk_size = pd.Timedelta(days=90)
    current_start = start
    all_prices = []
    
    while current_start < end:
        chunk_end = min(current_start + chunk_size, end)
        try:
            chunk_prices = client.query_day_ahead_prices(
                country_code, 
                start=current_start,
                end=chunk_end
            )
            all_prices.append(chunk_prices)
            print(f"Retrieved: {current_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Error for period {current_start} to {chunk_end}: {e}")
        
        current_start = chunk_end
    print("\n")
    return pd.concat(all_prices) if all_prices else pd.DataFrame()

# Replace original DA query with:
DA = get_da_prices_chunked(client, country_code, start, end)
# Export to CSV for verification
#DA.to_csv('outfile_DA_2024_direct.csv', header=['DA_price'])


# Ensure lengths match before assigning index
if len(DA) == len(datetime_hourly):
    DA.index = datetime_hourly
else:
    print(f"Length mismatch: DA has {len(DA)} elements, datetime_hourly has {int(len(datetime_hourly))} elements \n")
    DA = DA.iloc[:len(datetime_hourly)]
    DA.index = datetime_hourly[:len(DA)]


print("Starting to retrieve imbalance prices in 15-min chunks:")
imb = client.query_imbalance_prices(country_code, start=start, end=end, psr_type=None)
imb.index = datetime_15min[:len(imb)]
#imb =  imb.drop('Short', axis=1)
#print("\n imbalance price is:")
#print(imb[:5])


#%% Process to 15-min resolution
DA_15min = pd.DataFrame(index=datetime_15min)
DA_15min['DA_price'] = DA.reindex(index=datetime_15min, method='ffill')




#%% Export dataframes to .xlsx or .csv with verification

# Create properly structured DataFrames

DA_combined = pd.DataFrame()
#DA_combined = DA
DA_combined['datetime'] = DA.index
DA_combined['DA_price'] = DA.values



#imb_combined = pd.DataFrame()
imb_combined = imb

#%% Combine datasets
imb_combined['DA_price'] = DA_15min['DA_price']
#print("\n nu met DA prijzen bij imb erbij:")
#print(imb.head())
#imb_combined['datetime'] = imb.index
#imb_combined['Long'] = imb['Long']
#imb_combined['Short'] = imb['Short']
#imb_combined['imb_price1'] = imb.iloc[:,0]
#imb_combined['imb_price2'] = imb.iloc[:,1]
#imb_combined['DA_price'] = imb['DA_price']


# Print first 5 rows of each DataFrame
#print("\nDA_combined first 5 rows:")
#print(DA_combined.head())
#print(DA_combined[-5:])

print("\nimb_combined first 5 rows:")
print(imb_combined.head())
print("imb_combined last 5 rows:")
print(imb_combined[-5:])
print("\n")

# Export verified DataFrames
# Create filename with dates
start_date_str = start.strftime('%Y%m%d')
end_date_str = end.strftime('%Y%m%d')

# Export with date-based filenames
DA_combined.to_csv(f'outfile_DA_60min_{country_code}_{start_date_str}_to_{end_date_str}.csv', index=False)
imb_combined.to_csv(f'outfile_imb_15min_{country_code}_{start_date_str}_to_{end_date_str}.csv')
print(f".csv files written for period {start_date_str} to {end_date_str}")

#%%
print(f"Length mismatch: DA has {len(DA_combined)} elements, imb_combined has {len(imb_combined)} = {len(imb_combined)/4}elements")
print("Script finished")