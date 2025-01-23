#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 19:59:37 2025

@author: chunhan
"""

from dash import html, register_page, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from utils import df

# Register the page
register_page(__name__, path="/")

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Define the layout for the home page
layout = html.Div([
    html.H2("Welcome to the Home Page"),
    html.P("This is the main page of the app."),
    dcc.RadioItems(options=["year", "month", "region"], value = "year", id= 'controls-and-radio-item'),
    dcc.Graph(figure={}, id='controls-and-graph'),
    html.Div([
        html.Br(),
        html.A("Go to Page 1", href="/page-1"),  # Navigation link back to home
        html.Br(),
        html.A("Go to login page", href="/login"),
        ])
])

# Add controls to build the interaction
@callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Input(component_id="controls-and-radio-item", component_property="value")
    )

def update_graph(col_chosen):
    agg_data = df.groupby(col_chosen)['kwh_per_acc'].mean().reset_index()
    # fig = px.histogram(df, x = col_chosen, y = "kwh_per_acc", histfunc="avg")
    fig = px.line(agg_data, x=col_chosen, y="kwh_per_acc")
    
    fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
    return fig