import os
import pandas as pd
import plotly.express as px
from entsoe import EntsoePandasClient

# Setup Environment
os.system('clear')  # Clear console (Linux/MacOS)

# Load API Key & Configurations
API_KEY = os.getenv("ENTSOE_API_KEY")
client = EntsoePandasClient(api_key=API_KEY)
COUNTRY_CODE = "NL"
DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_data(year):
    file_path = os.path.join(DATA_DIR, f"prices_{year}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path, index_col=0, parse_dates=True)
    
    start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    end = pd.Timestamp(f"{year}-12-31", tz="UTC")
    prices = client.query_day_ahead_prices(COUNTRY_CODE, start=start, end=end)
    prices.to_csv(file_path)
    return prices

# Loop Through Years (2019-2024)
data_frames = [fetch_data(year) for year in range(2019, 2025)]
all_data = pd.concat(data_frames)

# Compute Annual Average Prices
annual_avg = all_data.resample("Y").mean()

# Create Histogram
fig = px.histogram(all_data, x=all_data.values.flatten(), title="Price Distribution")
fig.add_scatter(x=annual_avg.index.year, y=annual_avg.values.flatten(), mode='markers', name='Annual Average')

# Save & Display
fig.write_html("price_histogram.html")
fig.show()