#%% import packages
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
import datetime
from entsoe import EntsoeRawClient
from entsoe import EntsoePandasClient

# Clear console (optional)
import os
os.system('clear')  # for Mac/Linux

# Load environment variables from .env file
from dotenv import load_dotenv
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
print(combined_data)

# Print the DataFrame
combined_data['time'] = pd.to_datetime(combined_data['time'], utc=True).dt.tz_convert('Europe/Amsterdam')
#combined_data = combined_data.drop(columns=['index'])

# Extract hour
combined_data.insert(1, 'hour', combined_data['time'].dt.hour)
#print(combined_data.head())


# Calculate annual average prices
annual_avg_prices = combined_data.groupby('year')['DA_price'].mean().reset_index()
annual_avg_prices = annual_avg_prices.rename(columns={'DA_price': 'Annual Average Price'})
print("Annual Average Prices:")
print(annual_avg_prices)
# Merge annual average prices into the combined data
#combined_data = pd.merge(combined_data, annual_avg_prices, on='year', how='left')

# Calculate hourly average prices
hourly_avg_prices = combined_data.groupby(['year', combined_data['time'].dt.hour])['DA_price'].mean().reset_index()
hourly_avg_prices = hourly_avg_prices.rename(columns={'DA_hour_avg_price': 'Hourly Average Price'})
hourly_avg_prices['DA_price'] = hourly_avg_prices['DA_price'].round(1)

# Pivot the table to have years as columns and hours as rows
hourly_avg_prices = hourly_avg_prices.pivot(index='time', columns='year', values='DA_price')
hourly_avg_prices = hourly_avg_prices.reset_index()
#hourly_avg_prices = hourly_avg_prices.rename(columns={'year': 'hour'})
# Calculate the average of each row and add it as a new column
hourly_avg_prices['Average'] = hourly_avg_prices.mean(axis=1).round(1)

print("Hourly Average Prices:")
print(hourly_avg_prices)




# New:
df = combined_data.copy()

average_price_per_hour = hourly_avg_prices[['time', 2024]].copy()
average_price_per_hour.rename(columns={2024: 'DA_price'}, inplace=True)
average_price_per_hour['hour'] = average_price_per_hour['time']
average_price_per_hour = average_price_per_hour.drop(columns=['time'])
print(average_price_per_hour)


# calculate price difference between 11-16h and 20h-08h
price_diff = average_price_per_hour[(average_price_per_hour['hour'] >= 11) & (average_price_per_hour['hour'] <= 16)]['DA_price'].mean() - average_price_per_hour[(average_price_per_hour['hour'] >= 20) | (average_price_per_hour['hour'] <= 8)]['DA_price'].mean()
print(f"Price difference in year 2024 between 11-16h and 20h-08h: {price_diff:.0f} €/MWh")

# calculate price difference between cheapest 2 hours between 10-17h and most 6 expensive hours betweeb 17h-09h
cheapest_hours = average_price_per_hour[(average_price_per_hour['hour'] >= 10) & (average_price_per_hour['hour'] <= 17)]['DA_price'].nsmallest(3).mean()
most_expensive_hours = average_price_per_hour[(average_price_per_hour['hour'] >= 17) | (average_price_per_hour['hour'] <= 9)]['DA_price'].nlargest(8).mean()
price_diff = cheapest_hours - most_expensive_hours
print(f"Price difference in year 2024 between cheapest 3 hours between 10-17h and most expensive 8 hours between 17h-09h: {price_diff:.0f} €/MWh")




from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

# Create subplots
fig = make_subplots(rows=3, cols=1, subplot_titles=('Price over Time', 'Average Price per Hour','Price Distribution'),)

# Add the first plot (Price over Time)
fig.add_trace(go.Scatter(x=df['time'], y=df['DA_price'], mode='lines', name='DA Price 2024'), row=1, col=1)

# Add traces for each year in hourly_avg_prices
for column in hourly_avg_prices.columns:
    if column != 'time' and column != 'Average':
        fig.add_trace(go.Scatter(x=hourly_avg_prices['time'], y=hourly_avg_prices[column], mode='lines', name=str(column)), row=2, col=1)


# Add the third plot (Histogram of Prices)
for year in years:
    fig.add_trace(go.Histogram(x=combined_data[combined_data['year'] == year]['DA_price'], name=f'Price Distribution {year}'), row=3, col=1)


# Update x-axis title
fig.update_xaxes(title_text="Hour of the Day", row=2, col=1)
fig.update_xaxes(title_text="Electricity price €/MWh", row=3, col=1)

# Update y-axis title
fig.update_yaxes(title_text="Electricity price €/MWh", row=1, col=1)
fig.update_yaxes(title_text="Electricity price €/MWh", row=2, col=1)
fig.update_yaxes(title_text="Frequency [hours/year]", row=3, col=1)

# Update layout with a title and axis labels
fig.update_layout(title='EPEX Prices Analysis',
                  xaxis_title='Time',
                  yaxis_title='Electricity price €/MWh')

# Show the plot
fig.show()
fig.write_html("EPEX_Prices_Analysis.html")

# Save as PDF
fig.write_image('EPEX_Prices_Analysis.pdf', width=800, height=1122)
