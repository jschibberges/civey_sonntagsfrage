#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

@st.cache_data
def loadData():
    # Define file path
    file_path = "data.csv"
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Load the CSV file
        data = pd.read_csv(file_path, parse_dates=['timestamp'])  # Assuming 'date' column contains dates
        data.set_index('date', inplace=True)  # Set 'date' as the index for easier plotting
        return data
    else:
        raise ValueError("No file present.")

st.title('Civey: Trends Sonntagsfrage') 
st.subheader(f'Status: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}')

data = loadData()
columns_to_drop = ["timestamp", "question", "error_margin"]
df = data.drop(columns=columns_to_drop)
st.line_chart(data=df)