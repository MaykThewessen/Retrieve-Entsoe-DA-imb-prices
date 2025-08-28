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

#%% Retrieve FCR prices for 2024 and save to CSV using EntsoeRawClient
start = pd.Timestamp('2024-01-01', tz='Europe/Amsterdam')
end = pd.Timestamp('2025-01-01', tz='Europe/Amsterdam')

raw_client = EntsoeRawClient(api_key=api_key)

try:
    # Use query_fcr for FCR prices
    response = raw_client.query_fcr(
        country_code=country_code,
        start=start,
        end=end
    )
    # response is XML, parse as needed
    with open('FCR_prices_2024.xml', 'w') as f:
        f.write(response)
    print("FCR prices for 2024 saved to FCR_prices_2024.xml")
except Exception as e:
    print(f"Error retrieving FCR prices: {e}")


