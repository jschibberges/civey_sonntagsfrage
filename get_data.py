#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 08:51:25 2024

@author: julianschibberges
"""
import requests
import os
import pandas as pd
from datetime import datetime


#formatted_date = datetime.date.today().strftime("%y%m%d")


def getCurrentCiveyPoll(cid=37307):
    baseurl = "https://api.civey.com/v1/voter/polls/"
    r = requests.get(baseurl+str(cid))
    if r.status_code == requests.codes.ok:
        data = r.json()
        return data["poll"]
        '''
        with open(formatted_date+"_"+str(37307)+'.json', 'w') as file:
            json.dump(r.json(), file)
        '''

def transformCiveyPoll(data:dict):
    dic = {}
    dic["timestamp"] = int(datetime.timestamp(datetime.now()))
    dic["question"] = data["text"]
    for party in data["answers"]:
        if party["label"] == "NICHTWAEHLER":
            continue
        dic[party["label"]]=data["representative_result"]["result_ratios"][party["id"]]
    dic["date"] = data["representative_result"]["timeframe_to"][8:10]+"."+data["representative_result"]["timeframe_to"][5:7]+"."+data["representative_result"]["timeframe_to"][0:4]
    dic["error_margin"] = data["representative_result"]["error_margin"]
    dic = {key: [value] for key, value in dic.items()}
    return dic

def saveData(data:dict):
    # Define file path
    file_path = "data.csv"
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Load the CSV file
        data_loaded = pd.read_csv(file_path)
        
        # Append a new line (modify as needed)
        new_data = pd.DataFrame(data)  # Replace with actual data
        df = pd.concat([data_loaded, new_data], ignore_index=True)
        
        # Save the updated file
        df.to_csv(file_path, index=False)
    else:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)


if __name__ == "__main__":
    saveData(transformCiveyPoll(getCurrentCiveyPoll(cid=37307)))

