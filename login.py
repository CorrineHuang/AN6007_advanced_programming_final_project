#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 21:13:32 2025

@author: chunhan
"""

from dash import html, register_page

# Register the page
register_page(__name__, path="/login")

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Define the layout for Page 1
# layout = html.Div([
    # html.H1("WELCOME TO LOG IN"),  # Page-specific header
layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Welcome to login page',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.P("This is the log in page of the app."),
    html.Div([
        html.Br(),
        html.A("Go to Home Page", href="/"),  # Navigation link back to home
    ])
])