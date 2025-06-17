import requests
import pandas as pd

@st.cache_data(ttl=86400)
def get_all_countries():
    url = "http://api.worldbank.org/v2/country?format=json&per_page=500"
    response = requests.get(url)
    if response.status_code != 200:
        return {}
    
    data = response.json()[1]
    return {item["name"]: item["id"] for item in data if item["region"]["value"] != "Aggregates"}
