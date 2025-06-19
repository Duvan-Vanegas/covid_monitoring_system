"""Extracting COVID-19 data from https://disease.sh/v3/covid-19"""

import os
import time
import json
import requests

# Base API URL
BASE_URL = "https://disease.sh/v3/covid-19"

# Directory to store raw data
RAW_DATA_DIR = "data/raw"

# Endpoints to extract data
ENDPOINTS = {
    "countries": "countries",
    "historical": "historical/all?lastdays=all"
}


def fetch_data(endpoint, retries=3, backoff=5):
    """
    Make a GET request to an API endpoint.
    Requirement:
        Retries with backoff
    """
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[{endpoint}] Error: {e}")
            if attempt < retries - 1:
                print(f"Reintentando en {backoff} segundos...")
                time.sleep(backoff)
            else:
                raise


def save_raw_data(name, data):
    """
    Save the obtained data in JSON format to a local file.
    Requirements:
        Storage in temporary JSON format
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    path = os.path.join(RAW_DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Datos guardados: {path}")


def run():
    """
    Main function to run the data extraction pipeline.
    """
    print("Extrayendo datos COVID-19...")

    countries = fetch_data(ENDPOINTS["countries"])
    historical = fetch_data(ENDPOINTS["historical"])

    save_raw_data("countries", countries)
    save_raw_data("historical", historical)

    print("Extracción completada!")

if __name__ == "__main__":
    run()
