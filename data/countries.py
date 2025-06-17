# data/countries.py
import requests

def get_all_countries():
    response = requests.get("https://api.worldbank.org/v2/country?format=json&per_page=300")
    data = response.json()[1]

    countries = {}
    for entry in data:
        code = entry["id"]
        name = entry["name"]
        countries[name] = code

    return countries
