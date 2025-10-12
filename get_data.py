#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script fetches the latest German federal election poll data from the Civey API,
transforms it, and appends it to a CSV file.
"""
import requests
import os
import pandas as pd
from datetime import datetime

# --- Constants ---
API_BASE_URL = "https://api.civey.com/v1/voter/polls/"
POLL_ID = 37307
DATA_FILE_PATH = "data.csv"
EXCLUDED_PARTIES = {"NICHTWAEHLER"}

def get_current_civey_poll(cid: int) -> dict:
    """Fetches a specific poll from the Civey API."""
    url = f"{API_BASE_URL}{cid}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get("poll", {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Civey API: {e}")
        raise

def transform_civey_poll(poll_data: dict) -> dict:
    """Transforms the raw API poll data into a structured format for our CSV."""
    if not poll_data or "representative_result" not in poll_data:
        print("Warning: Received empty or malformed poll data.")
        return {}

    rep_result = poll_data["representative_result"]
    
    # Parse date and format to YYYY-MM-DD for consistency and sortability
    try:
        date_str = rep_result.get("timeframe_to", "")
        # Take only the date part (e.g., '2024-01-15' from '2024-01-15T23:59:59+01:00')
        iso_date = date_str.split('T')[0]
        datetime.strptime(iso_date, '%Y-%m-%d') # Validate format
    except (ValueError, IndexError):
        print(f"Warning: Could not parse date from '{date_str}'. Skipping this data point.")
        return {}

    transformed_data = {
        "timestamp": int(datetime.now().timestamp()),
        "date": iso_date,
        "question": poll_data.get("text"),
        "error_margin": rep_result.get("error_margin")
    }

    result_ratios = rep_result.get("result_ratios", {})
    for party in poll_data.get("answers", []):
        party_label = party.get("label")
        if party_label in EXCLUDED_PARTIES:
            continue
        
        party_id = party.get("id")
        if party_label and party_id in result_ratios:
            transformed_data[party_label] = result_ratios[party_id]

    # Convert scalar values to lists for DataFrame creation
    return {key: [value] for key, value in transformed_data.items()}

def save_data(data: dict):
    """Appends the transformed data to the CSV file."""
    if not data:
        print("No data to save.")
        return

    new_df = pd.DataFrame(data)
    
    try:
        if os.path.exists(DATA_FILE_PATH):
            # Read existing headers to ensure column order is maintained
            existing_df = pd.read_csv(DATA_FILE_PATH, nrows=0)
            # Reorder new data to match existing file's column order
            # This handles cases where the API might change the order of parties
            new_df = new_df.reindex(columns=existing_df.columns)

            # Append without writing header
            new_df.to_csv(DATA_FILE_PATH, mode='a', header=False, index=False)
            print(f"Successfully appended new data to {DATA_FILE_PATH}.")
        else:
            # Create new file with header
            new_df.to_csv(DATA_FILE_PATH, index=False)
            print(f"Successfully created and saved data to {DATA_FILE_PATH}.")
    except IOError as e:
        print(f"Error writing to file {DATA_FILE_PATH}: {e}")
        raise

if __name__ == "__main__":
    try:
        raw_poll = get_current_civey_poll(cid=POLL_ID)
        if raw_poll:
            transformed_data = transform_civey_poll(raw_poll)
            save_data(transformed_data)
    except Exception as e:
        print(f"An error occurred during the data update process: {e}")
