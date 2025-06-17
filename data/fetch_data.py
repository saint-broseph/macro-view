# data/fetch_data.py
import requests
import pandas as pd

def fetch_indicator(country_code, indicator_code, years=10):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=100"
    response = requests.get(url)
    
    if response.status_code != 200 or not response.json() or len(response.json()) < 2:
        return pd.DataFrame(columns=["Year", "Value"])
    
    data = response.json()[1]
    df = pd.DataFrame(data)[['date', 'value']]
    df.columns = ['Year', 'Value']
    df.dropna(inplace=True)
    df['Year'] = df['Year'].astype(int)
    df = df[df['Year'] >= (df['Year'].max() - years + 1)]
    return df[::-1]  # reverse for chronological order
