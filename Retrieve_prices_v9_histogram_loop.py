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




#%% Create a histogram using plotly
import plotly.express as px

# Define the years you want to analyze
years = [2024, 2023, 2022, 2021, 2020, 2019]

# Initialize an empty DataFrame to store data for all years
all_data = []

# Loop through each year and retrieve data
for year in years:
    start = pd.Timestamp(f'{year}-01-01 00:00:00', tz='Europe/Brussels')
    end = pd.Timestamp(f'{year}-12-31 23:59:59', tz='Europe/Brussels')
    
    # Retrieve Day-Ahead prices for the year
    DA = get_da_prices_chunked(client, country_code, start, end)
    DA.rename(columns={DA.columns[0]: 'time', DA.columns[1]: 'DA_price'}, inplace=True)
    
    # Add a 'year' column to distinguish data
    DA['year'] = year
    all_data.append(DA)

# Combine all years into a single DataFrame
combined_data = pd.concat(all_data)

# Check if combined_data contains data
if not combined_data.empty:
    # Create a histogram with different colors for each year
    fig = px.histogram(
        combined_data,
        x="DA_price",
        color="year",
        opacity=0.6,  # Set opacity for overlapping histograms
        title="Histogram of Day-Ahead Prices for Multiple Years",
        labels={"DA_price": "Day-Ahead Price (EUR/MWh)", "year": "Year"},
        barmode="overlay"  # Overlay histograms
    )
    fig.update_layout(
        xaxis_title="Day-Ahead Price (EUR/MWh)",
        yaxis_title="Frequency (hours/year)",
        template="plotly_white"
    )
    
    # Generate filename with year range and current date
    start_year = min(years)
    end_year = max(years)
    today_date = datetime.date.today().strftime("%Y%m%d")
    filename = f"DA_price_histogram_ran_{today_date}_range_{start_year}-{end_year}.html"
    
    # Save the plot to a file
    fig.write_html(filename)
    
    fig.show()
    print(f"Histogram for multiple years created and saved to {filename}")
else:
    print("No data available to create a histogram.")






