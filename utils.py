#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 22:16:42 2025

@author: chunhan
"""
import pandas as pd
from flask import jsonify
import json
import random 
# df=pd.read_csv("final.csv")

def pretty_jsonify(*args, **kwargs):
    response = jsonify(*args, **kwargs)
    response.data = json.dumps(json.loads(response.data), indent=4)  # Pretty print JSON
    response.mimetype = 'application/json'
    return response

def generate_new_meter_id(accounts):
    while True:
        meter_id = ''
        for i in range(11):
            if i in [3, 7]:
                meter_id += '-'
            else:
                meter_id += str(random.randint(0,9))
        if meter_id not in accounts:
            return meter_id 