#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 19:47:49 2025

@author: chunhan
"""
from dash import Dash, html, dcc
import pandas as pd
import dash

# Initialize the app
app = Dash(__name__, use_pages=True)

# Define the main layout with only the page container
app.layout = html.Div([
    dash.page_container  # This renders the content of the current page
])

if __name__ == "__main__":
    app.run_server(debug=True)