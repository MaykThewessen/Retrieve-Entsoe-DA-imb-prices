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
years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

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
        # If it's the current year, set the end date to yesterday
        if year == datetime.datetime.now().year:
            end = pd.Timestamp(datetime.date.today() - datetime.timedelta(days=1), tz='Europe/Brussels')
        else:
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
df = pd.concat(all_data)
print("df:")
print(df)

# Print the DataFrame
df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert('Europe/Amsterdam')
#df = df.drop(columns=['index'])

# Extract hour
df.insert(1, 'hour', df['time'].dt.hour)
#print(df.head())


# Calculate annual average prices
annual_avg_prices = df.groupby('year')['DA_price'].mean().round(1).reset_index()
annual_avg_prices = annual_avg_prices.set_index('year') # Set 'year' as index
annual_avg_prices = annual_avg_prices.rename(columns={'DA_price': 'Annual Average'})
print("Annual Average Prices:")
print(annual_avg_prices)


# Calculate hourly average prices
hourly_avg_prices = df.groupby(['year', df['time'].dt.hour])['DA_price'].mean().reset_index()
hourly_avg_prices = hourly_avg_prices.rename(columns={'DA_hour_avg_price': 'Hourly Average Price'})
hourly_avg_prices['DA_price'] = hourly_avg_prices['DA_price'].round(1)

# Pivot the table to have years as columns and hours as rows
hourly_avg_prices = hourly_avg_prices.pivot(index='time', columns='year', values='DA_price')
hourly_avg_prices = hourly_avg_prices.reset_index()
hourly_avg_prices = hourly_avg_prices.rename(columns={'time': 'hour'})
# Calculate the average of each row and add it as a new column
hourly_avg_prices['Average'] = hourly_avg_prices.mean(axis=1).round(1)
#hourly_avg_prices = hourly_avg_prices.set_index('hour')
print("Hourly Average Prices:")
print(hourly_avg_prices)




# calculate price difference between 11-16h and 20h-08h
year_select = 2024
h_avg_selected = hourly_avg_prices[['hour', year_select]]
h_avg_selected = h_avg_selected.rename(columns={year_select: 'DA_price'})
#print(f"h_avg_selected {year_select}:")
#print(h_avg_selected)


price_diff = h_avg_selected[(h_avg_selected['hour'] >= 11) & (h_avg_selected['hour'] <= 16)]['DA_price'].mean() - h_avg_selected[(h_avg_selected['hour'] >= 20) | (h_avg_selected['hour'] <= 8)]['DA_price'].mean()
print(f"Price difference in year {year_select} between 11-16h and 20h-08h: {price_diff:.0f} €/MWh")


# calculate price difference between cheapest 2 hours between 10-17h and most 6 expensive hours betweeb 17h-09h
h_avg_selected_10_17 = h_avg_selected[(h_avg_selected['hour'] >= 10) & (h_avg_selected['hour'] <= 17)]
cheapest_hours = h_avg_selected_10_17['DA_price'].nsmallest(3).mean()

h_avg_selected_17_09 = h_avg_selected[(h_avg_selected['hour'] >= 17) | (h_avg_selected['hour'] <= 9)]
most_expensive_hours = h_avg_selected_17_09['DA_price'].nlargest(8).mean()

price_diff_2 = cheapest_hours - most_expensive_hours
print(f"Price difference in year {year_select} between cheapest 3 hours between 10-17h and most expensive 8 hours between 17h-09h: {price_diff_2:.0f} €/MWh")

# calculate price difference between cheapest 2 hours between 10-17h and most 6 expensive hours betweeb 17h-09h
#cheapest_hours = price_diff[(h_avg_selected['hour'] >= 10) & (h_avg_selected['hour'] <= 17)]['DA_price'].nsmallest(3).mean()
#most_expensive_hours = h_avg_selected[(h_avg_selected['hour'] >= 17) | (h_avg_selected['hour'] <= 9)]['DA_price'].nlargest(8).mean()
#price_diff = cheapest_hours - most_expensive_hours
#print(f"Price difference in year {year_select} between cheapest 3 hours between 10-17h and most expensive 8 hours between 17h-09h: {price_diff:.0f} €/MWh")




from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

# Create subplots
fig = make_subplots(rows=4, cols=1, subplot_titles=('Day-Ahead Electricity Price over time', 'Average Price per Hour for various years', 'Average Price per Hour by Month for year 2024','DA Price Distribution'),)

# Add the first plot (Price over Time)
fig.add_trace(go.Scatter(x=df['time'], y=df['DA_price'], mode='lines', name='Day-Ahead hourly price'), row=1, col=1)

# Add traces for each year in hourly_avg_prices
for column in hourly_avg_prices.columns:
    if column != 'hour' and column != 'Average':
        fig.add_trace(go.Scatter(x=hourly_avg_prices['hour'], y=hourly_avg_prices[column], mode='lines', name=f'Year {column}'), row=2, col=1)


# Filter data for the year 2024
df_2024 = df[df['year'] == 2024].copy()
# Drop the 'year' column
df_2024.drop(columns=['year'], inplace=True)
df_2024['month'] = df_2024['time'].dt.month
print("df_2024:")
print(df_2024)

# Add the third plot (Average Price per Hour by month)
# Group by month
monthly_hourly_avg_prices = df_2024.groupby(['month', 'hour'])['DA_price'].mean().round(1).unstack()
print("monthly_hourly_avg_prices:")
print(monthly_hourly_avg_prices)





import plotly.io as pio

# Configure plotly to not include MathJax
pio.kaleido.scope.mathjax = None

# Plot 1: Day-Ahead Electricity Price over time
fig1 = px.line(df, x='time', y='DA_price', title=f'Day-Ahead Electricity Price NL:')
fig1.update_xaxes(title_text="Time")
fig1.update_yaxes(title_text="Electricity price €/MWh")
pio.write_image(fig1, 'DA_Price_Time_Series.pdf', width=800, height=600)

# Plot 2: Average Price per Hour for various years
fig2 = go.Figure()
for year in [2019, 2022, 2025]:
    if year in hourly_avg_prices.columns:
        fig2.add_trace(go.Scatter(x=hourly_avg_prices['hour'], y=hourly_avg_prices[year], mode='lines', name=f'Year {year}'))
fig2.update_layout(title=f'Average Dynamic EPEX Price NL per Hour:',
                   xaxis_title='Hour of the Day',
                   yaxis_title='Electricity price €/MWh')
pio.write_image(fig2, 'Hourly_Avg_Prices_by_Year.pdf', width=800, height=600)

# Plot 3: Average Price per Hour by Month for year 2024
fig3 = go.Figure()
for month in [1, 4, 12]:
    month_data = monthly_hourly_avg_prices.loc[month]
    fig3.add_trace(go.Scatter(x=monthly_hourly_avg_prices.columns, y=month_data, mode='lines', name=f'Month {month} {year_select}'))
fig3.update_layout(title=f'Average Price per Hour per Month of 2024',
                   xaxis_title='Hour of the Day',
                   yaxis_title='Electricity price €/MWh')
pio.write_image(fig3, 'Hourly_Avg_Prices_by_Month_2024.pdf', width=800, height=600)

# Plot 4: Histogram of Prices
fig4 = go.Figure()
for year in years:
    fig4.add_trace(go.Histogram(x=df[df['year'] == year]['DA_price'], name=f'Price Distribution {year}'))
fig4.update_layout(title=f'DA Price Distribution - {datetime.datetime.now().strftime("%Y-%m-%d")}',
                   xaxis_title='Electricity price €/MWh',
                   yaxis_title='Frequency [hours/year]')
pio.write_image(fig4, 'DA_Price_Distribution.pdf', width=800, height=600)

# Plot 5: Annual Average Prices
fig5 = go.Figure(data=[go.Bar(x=annual_avg_prices.index, y=annual_avg_prices['Annual Average'])])
fig5.update_layout(title=f'Annual Average Day-Ahead Electricity Prices',
                   xaxis_title='Year',
                   yaxis_title='Electricity price €/MWh')
pio.write_image(fig5, 'Annual_Average_Prices.pdf', width=800, height=600)

import plotly.io as pio
# Configure plotly to not include MathJax
pio.kaleido.scope.mathjax = None
pio.write_image(fig, 'EPEX_Prices_Analysis_v4.html', width=800, height=1122)

