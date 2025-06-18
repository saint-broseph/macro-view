import requests
import pandas as pd

def fetch_indicator(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=1000"
    response = requests.get(url)

    if response.status_code != 200:
        return pd.DataFrame()  # return empty DataFrame if error

    try:
        data = response.json()[1]
        if data is None:
            return pd.DataFrame()

        records = []
        for item in data:
            if item.get('value') is not None:
                records.append({
                    'Year': int(item['date']),
                    'Value': float(item['value'])
                })

        df = pd.DataFrame(records)
        return df.sort_values("Year")

    except (IndexError, ValueError, TypeError, KeyError):
        return pd.DataFrame()
