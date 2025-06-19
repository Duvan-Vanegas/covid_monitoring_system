"""Transformation of raw COVID-19 data."""

import os
import json
import pandas as pd

# Directories
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def transform_data():
    """
    Data cleaning
    Reads raw JSON files and returns cleaned DataFrames for database storage.
    """

    # Clean countries
    with open(os.path.join(RAW_DIR, "countries.json"), encoding="utf-8") as f:
        countries_raw = json.load(f)

    df_current = pd.json_normalize(countries_raw)[[
        "country", "cases", "active", "deaths", "recovered", "updated",
        "countryInfo.lat", "countryInfo.long"
    ]].copy()
    
    df_current.rename(columns={
        "countryInfo.lat": "lat",
        "countryInfo.long": "long"
    }, inplace=True)

    df_current["country"] = df_current["country"].astype(str)
    df_current.fillna(0, inplace=True)
    df_current["updated"] = pd.to_datetime(df_current["updated"], unit="ms")

    # Clean historical
    with open(os.path.join(RAW_DIR, "historical.json"), encoding="utf-8") as f:
        historical_raw = json.load(f)

    df_historical = pd.DataFrame({
        "date": list(historical_raw["cases"].keys()),
        "cases": list(historical_raw["cases"].values()),
        "deaths": list(historical_raw["deaths"].values()),
    })

    df_historical["date"] = pd.to_datetime(df_historical["date"], format="%m/%d/%y")
    df_historical = df_historical.sort_values("date").reset_index(drop=True)
    df_historical["country"] = "Global"

    # Structure for db - SQLite
    df_current = df_current[[
        "country", "cases", "active", "deaths", "recovered", "updated", "lat", "long"
    ]]
    df_historical = df_historical[["date", "country", "cases", "deaths"]]

    return {
        "current_data": df_current,
        "historical_data": df_historical
    }


def run():
    """
    Runs transformation and writes output to CSV.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    data = transform_data()

    data["current_data"].to_csv(os.path.join(PROCESSED_DIR, "current_data.csv"), index=False)
    data["historical_data"].to_csv(os.path.join(PROCESSED_DIR, "historical_data.csv"), index=False)

    print("Transformación completada. CSVs generados en data/processed.")

if __name__ == "__main__":
    run()
