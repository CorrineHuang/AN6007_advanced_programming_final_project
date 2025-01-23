#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 20:07:20 2025

@author: chunhan
"""

from dash import html, register_page

# Register the page
register_page(__name__, path="/page-1")

# Define the layout for Page 1
layout = html.Div([
    html.H1("Page 1"),  # Page-specific header
    html.P("This is Page 1 of the app."),
    html.Div([
        html.Br(),
        html.A("Go to Home Page", href="/"),  # Navigation link back to home
    ])
])