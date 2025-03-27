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






#%% Retrieve and save/load data for multiple years

# Define years to analyze
years = [2019, 2020, 2021, 2022, 2023, 2024]

# Initialize an empty DataFrame to store data for all years
all_data = []

# Define the directory to save/load the data
data_dir = '/Users/mayk/Documents/GitHub/Retrieve-Entsoe-DA-imb-prices/data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Loop through each year and retrieve/load data; Data will be retrieved by Entso-e API, if not available in the data directory, else sourced locally from the data directory to save time!
for year in years:
    file_path = os.path.join(data_dir, f'DA_prices_{year}.csv')
    
    if os.path.exists(file_path):
        print(f"Loading year data: {year} locally from {file_path}")
        DA = pd.read_csv(file_path)
    else:
        print("Data not found in folder, Retrieving data for year: {year} from Entso-e API")
        start = pd.Timestamp(f'{year}-01-01 00:00:00', tz='Europe/Brussels')
        end = pd.Timestamp(f'{year}-12-31 23:59:59', tz='Europe/Brussels')
        
        # Retrieve Day-Ahead prices for the year
        DA = get_da_prices_chunked(client, country_code, start, end)
        DA.rename(columns={DA.columns[0]: 'time', DA.columns[1]: 'DA_price'}, inplace=True)
        
        # Save the data to a CSV file
        DA.to_csv(file_path, index=False)
        print(f"Saved data to {file_path}")
    
    # Add a 'year' column to distinguish data
    DA['year'] = year
    all_data.append(DA)

# Combine all years into a single DataFrame
combined_data = pd.concat(all_data)

# Calculate annual average prices
annual_avg_prices = combined_data.groupby('year')['DA_price'].mean().reset_index()
annual_avg_prices = annual_avg_prices.rename(columns={'DA_price': 'Annual Average Price'})

# Merge annual average prices into the combined data
combined_data = pd.merge(combined_data, annual_avg_prices, on='year', how='left')

#%% Create a histogram using plotly
import plotly.express as px


# Create a histogram with different colors for each year and fixed bin width
fig = px.histogram(
    combined_data,
    x="DA_price",
    color="year",
    opacity=0.5,  # Set opacity for overlapping histograms
    title=f"Histogram of Day-Ahead Prices for Multiple Years ({country_code})",
    labels={"DA_price": "Day-Ahead Price (EUR/MWh)", "year": "Year", "Annual Average Price": "Annual Average Price"},
    barmode="overlay",  # Overlay histograms
    hover_data=['Annual Average Price'],  # Show annual average price on hover
    nbins=None,  # Let Plotly calculate the number of bins
    histnorm=None  # No normalization
)
# Update the traces to set fixed bin width of 10 EUR/MWh
fig.update_traces(xbins=dict(size=10))


# Update the legend text to include the annual average price
for i, year in enumerate(years):
    avg_price = annual_avg_prices[annual_avg_prices['year'] == year]['Annual Average Price'].values[0]
    fig.data[i].name = f"{year} (avg: €{avg_price:.0f}/MWh)"

fig.update_layout(
    xaxis_title="Day-Ahead Price (EUR/MWh)",
    yaxis_title="Frequency (hours/year)",
    template="plotly_white",
    # Add axis range limits
    xaxis_range=[-200, 0],
    yaxis_range=[0, 100]
)


# Generate filename with year range and current date
start_year = min(years)
end_year = max(years)
today_date = datetime.date.today().strftime("%Y%m%d")
filename = f"DA_price_histogram_ran_{today_date}_range_{start_year}-{end_year}.html"

# Save the plot to a file
fig.write_html(filename)
print(f"Histogram for multiple years created and saved to {filename}")
fig.show()






