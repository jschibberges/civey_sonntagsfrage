#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- Page Configuration ---
# Use the wide layout for more space and set a title for the browser tab.
st.set_page_config(layout="wide", page_title="Civey Sonntagsfrage Tracker")

@st.cache_data
def load_data():
    """Loads data from data.csv, robustly parsing dates and setting index."""
    file_path = "data.csv"
    
    if not os.path.exists(file_path):
        st.error("Data file 'data.csv' not found. The data update might not have run yet.")
        return pd.DataFrame() # Return an empty DataFrame to prevent further errors

    try:
        data = pd.read_csv(file_path)
        
        # Explicitly handle mixed date formats to be more robust.
        # First, try parsing the new format (YYYY-MM-DD).
        parsed_dates = pd.to_datetime(data['date'], format='%Y-%m-%d', errors='coerce')
        
        # For rows that failed, try parsing the old format (DD.MM.YYYY).
        failed_indices = parsed_dates.isna()
        if failed_indices.any():
            parsed_dates.loc[failed_indices] = pd.to_datetime(
                data.loc[failed_indices, 'date'], format='%d.%m.%Y', errors='coerce'
            )
        
        data['date'] = parsed_dates
        
        # Drop rows where the date could not be parsed in either format.
        original_rows = len(data)
        data.dropna(subset=['date'], inplace=True)
        dropped_rows = original_rows - len(data)
        if dropped_rows > 0:
            st.warning(
                f"Removed {dropped_rows} corrupted or unparseable row(s) from the data. "
                f"Please run the `migrate_csv_layout.py` script to clean your `data.csv` file."
            )

        if data.empty:
            st.error("No valid data could be loaded from 'data.csv'.")
            return pd.DataFrame()

        data.set_index('date', inplace=True)
        data.sort_index(inplace=True) # Ensure data is sorted by date
        return data
    except Exception as e:
        st.error(f"An unexpected error occurred while loading 'data.csv': {e}")
        return pd.DataFrame()

st.title('Civey: Trends Sonntagsfrage') 

data = load_data()

if not data.empty:
    # --- Header ---
    # Display the date of the latest data point for more context.
    latest_date = data.index[-1]
    st.subheader(f"Letzte Daten vom: {latest_date.strftime('%d.%m.%Y')}")
    st.write("---")

    # --- Key Metrics ---
    # Show the latest poll numbers and the change from the previous day.
    st.subheader("Aktuelle Umfragewerte")
    st.caption("Die prozentuale Veränderung vergleicht den aktuellen Wert mit dem Wert von vor ca. einem Monat.")
    
    party_cols = [c for c in data.columns if c not in ["timestamp", "question", "error_margin"]]
    
    # Get latest data point
    latest_data = data.iloc[-1]

    # Find data from one month ago for comparison
    one_month_ago_date = latest_data.name - pd.DateOffset(months=1)

    # Find the closest available date in the index to one_month_ago_date.
    if len(data) > 1:
        # To find the closest date, we create a Series of the absolute time
        # differences between each date in the index and our target date.
        time_diffs = pd.Series(abs(data.index - one_month_ago_date), index=data.index)
        # .idxmin() on this Series gives us the index label (the date) of the minimum value.
        comparison_date = time_diffs.idxmin()
        comparison_data = data.loc[comparison_date]
    else:
        # If only one data point, compare against itself (delta will be 0)
        comparison_data = latest_data

    # Display metrics in columns
    metric_cols = st.columns(6)
    parties_for_metrics = ['CDU_CSU', 'SPD', 'GRUENE', 'AFD', 'FDP', 'BSW']
    for i, party in enumerate(parties_for_metrics):
        if party in latest_data:
            val = latest_data[party]
            delta = val - comparison_data[party]
            metric_cols[i].metric(
                label=party,
                value=f"{val:.1%}",
                delta=f"{delta:.2%}"
            )

    # --- Interactive Chart ---
    st.write("---")
    st.subheader("Trend über Zeit")

    party_colors = {
        "CDU_CSU": "#000000", "SPD": "#EB001F", "GRUENE": "#64A12D",
        "FDP": "#FFED00", "AFD": "#009EE0", "LINKE": "#BE3075",
        "BSW": "#E4007C", "FW": "#FF8000", "SONSTIGE": "grey"
    }

    # Allow user to select which parties to display
    selected_parties = st.multiselect(
        "Parteien auswählen:",
        options=party_cols,
        default=['CDU_CSU', 'SPD', 'GRUENE', 'AFD', 'FDP'] # Sensible defaults
    )

    if selected_parties:
        # Use Plotly for a richer, more interactive chart
        plot_df = data[selected_parties] * 100 # Convert to percentage for display
        fig = px.line(plot_df, x=plot_df.index, y=selected_parties, color_discrete_map=party_colors)
        
        fig.update_layout(yaxis_title="Prozent", xaxis_title="Datum", legend_title_text='Parteien')
        fig.update_traces(hovertemplate='%{y:.1f}%') # Custom tooltip format
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Bitte wählen Sie mindestens eine Partei aus, um den Graphen anzuzeigen.")

    # --- Data Details Expander ---
    st.write("---")
    with st.expander("Details und Rohdaten anzeigen"):
        st.markdown(f"**Frage:** *{data['question'].iloc[-1]}*")
        st.markdown(f"**Statistischer Fehlerbereich:** *+/- {data['error_margin'].iloc[-1]:.1%}*")
        st.subheader("Rohdaten")
        st.dataframe(data)