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

print("Script started to retrieve Day-Ahead prices using Python and Entso-e API script")
start = pd.Timestamp('2024-01-01 00:00:00', tz='Europe/Brussels')
end   = pd.Timestamp('2025-01-01 00:00:00', tz='Europe/Brussels')
print(f"Start date: {start.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"End date:   {end.strftime('%Y-%m-%d %H:%M:%S')}")
country_code = 'NL'  # Netherlands



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
            # Ensure datetime is included as a column
            chunk_prices = chunk_prices.reset_index()  # Reset index to make datetime a column
            all_prices.append(chunk_prices)
            print(f"Retrieved: {current_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Error for period {current_start} to {chunk_end}: {e}")
        
        current_start = chunk_end
    print("\n")
    return pd.concat(all_prices) if all_prices else pd.DataFrame()

#%%  Create datetime arrays first
datetime_hourly = pd.date_range(start=start, end=end, freq='h', tz='Europe/Brussels')  # Using 'h' instead of 'H'

# Print the first few entries to verify
print("\n datetime_hourly first rows:")
print(datetime_hourly[:2])
print("\n datetime_hourly last rows:")
print(datetime_hourly[-2:])
print("\n")

# Create a DataFrame with the datetime_hourly array
tijd = pd.DataFrame(datetime_hourly, columns=['datetime'])

# Replace original DA query with:
DA = get_da_prices_chunked(client, country_code, start, end)

# Rename the columns
DA.rename(columns={DA.columns[0]: 'time', DA.columns[1]: 'DA_price'}, inplace=True)



# Display the first few rows of 'tijd' and 'DA' columns
    # print("\nPreview of 'tijd' column:")
    # print(tijd.head())
    # print("Type of 'tijd':", type(tijd))

print("\nPreview of 'DA' column:")
print(DA.head())
print("Type of 'DA':", type(DA))


# Merge the two DataFrames
# Ensure the DataFrame has 'tijd' as the first column and 'DA' as the second column
    #df = pd.DataFrame({
    #    'tijd': tijd['datetime'],  # First column
    #    'DA': DA['DA_price']       # Second column
    #})
#df = pd.merge(tijd, DA)


# Create filename with dates
start_date_str = start.strftime('%Y%m%d')
end_date_str = end.strftime('%Y%m%d')

# Export with date-based filenames
DA.to_csv(f'outfile_df_{country_code}_{start_date_str}_to_{end_date_str}.csv', index=True)
print(f".csv files written for period {start_date_str} to {end_date_str}")


#%% Create a histogram using plotly
import plotly.express as px

#DA = DA.DA_price



# Check if DA contains data
if not DA.empty:
    # Create a histogram of Day-Ahead prices with a bin width of 20
    fig = px.histogram(
        DA,
        x=DA.columns[1],  # Assuming the second column contains the prices
        title=f"Histogram of Day-Ahead Prices in ({country_code}) for year: {start.year}",
        labels={DA.columns[1]: "Day-Ahead Price (EUR/MWh)"}
    )
    #fig.update_traces(xbins=dict(start=0, end=DA[DA.columns[0]].max(), size=20))  # Set bin width to 20
    fig.update_layout(
        xaxis_title="Day-Ahead Price (EUR/MWh)",
        yaxis_title="Frequency (hours/year)",
        template="plotly_white"
    )
    fig.show()
else:
    print("No data available in DA to create a histogram.")

#%%
print("Script finished")






