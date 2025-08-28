import pandas as pd


# Read the CSV file into a pandas DataFrame
df = pd.read_csv('outfile_df_NL_20240101_to_20250101.csv')

# Print the DataFrame
df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert('Europe/Amsterdam')
df = df.drop(columns=['index'])

# Extract hour
df.insert(1, 'hour', df['time'].dt.hour)
print(df)


# Calculate the average price per hour
average_price_per_hour = df.groupby('hour')['DA_price'].mean().reset_index()
average_price_per_hour['DA_price'] = average_price_per_hour['DA_price'].round(1)
# Print the average price per hour
print(average_price_per_hour)

# calculate price difference between 11-16h and 20h-08h
price_diff = average_price_per_hour[(average_price_per_hour['hour'] >= 11) & (average_price_per_hour['hour'] <= 16)]['DA_price'].mean() - average_price_per_hour[(average_price_per_hour['hour'] >= 20) | (average_price_per_hour['hour'] <= 8)]['DA_price'].mean()
print(f"Price difference between 11-16h and 20h-08h: {price_diff:.0f} €/MWh")

# calculate price difference between cheapest 2 hours between 10-17h and most 6 expensive hours betweeb 17h-09h
cheapest_hours = average_price_per_hour[(average_price_per_hour['hour'] >= 10) & (average_price_per_hour['hour'] <= 17)]['DA_price'].nsmallest(3).mean()
most_expensive_hours = average_price_per_hour[(average_price_per_hour['hour'] >= 17) | (average_price_per_hour['hour'] <= 9)]['DA_price'].nlargest(8).mean()
price_diff = cheapest_hours - most_expensive_hours
print(f"Price difference between cheapest 3 hours between 10-17h and most expensive 8 hours between 17h-09h: {price_diff:.0f} €/MWh")




from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

# Create subplots
fig = make_subplots(rows=3, cols=1, subplot_titles=('Price over Time', 'Average Price per Hour','Price Distribution'),)

# Add the first plot (Price over Time)
fig.add_trace(go.Scatter(x=df['time'], y=df['DA_price'], mode='lines', name='DA Price 2024'), row=1, col=1)

# Add the second plot (Average Price per Hour)
fig.add_trace(go.Scatter(x=average_price_per_hour['hour'], y=average_price_per_hour['DA_price'], mode='lines', name='Average DA Price per hour'), row=2, col=1)


# Add the third plot (Histogram of Prices)
fig.add_trace(go.Histogram(x=df['DA_price'], name='Price Distribution'), row=3, col=1)

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
