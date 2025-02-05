#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 22:16:42 2025

@author: chunhan
"""
import pandas as pd
from flask import jsonify
import json

df=pd.read_csv("final.csv")

def pretty_jsonify(*args, **kwargs):
    response = jsonify(*args, **kwargs)
    response.data = json.dumps(json.loads(response.data), indent=4)  # Pretty print JSON
    response.mimetype = 'application/json'
    return response