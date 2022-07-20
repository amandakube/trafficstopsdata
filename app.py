from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache
import numpy as np
import json
from urllib.request import urlopen

register_page(__name__, icon="fas fa-bullseye")

grouped = pd.read_csv('static/hitrates_beat_district_race.csv')
grouped_norace = pd.read_csv('static/hitrates_beat_district.csv')

with urlopen('https://github.com/amandakube/trafficstopsdata/blob/4f771bf1d034f032b4edc5198870ded86df0549d/Boundaries-PoliceBeats(current).geojson?raw=true') as policebeats:
    gj = json.load(policebeats)

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': '1112'},{'customdata': '01'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='map'),
    ], style={'display': 'inline-block', 'width': '49%'}), 
html.Div([
    html.Div(dcc.RangeSlider(
        grouped_norace['YEAR'].min(),
        grouped_norace['YEAR'].max(),
        step=None,
        id='crossfilter-year--slider',
        value=[grouped_norace['YEAR'].min(), grouped_norace['YEAR'].max()],
        marks={str(year): str(year) for year in grouped_norace['YEAR'].unique()}
    ), style={'width': '49%', 'display': 'inline-block'}),
    dcc.Graph(id='race-scatter'),
    ], style={'display': 'inline', 'width': '49%'}),
    html.Div([
        dcc.Graph(id='race-scatter-dist'),
    ], style={'display': 'inline', 'width': '49%'}),
])


@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('crossfilter-year--slider', 'value'))
def update_graph(year_value):
    filter_mask = (grouped_norace['YEAR'] >= year_value[0]) & (grouped_norace['YEAR'] <= year_value[1])
    dat = grouped_norace[filter_mask]
    fig = px.scatter(dat, x="HITRATE", y="num_searches", color="District", hover_data=['Beat','YEAR','District'],
    labels={ "HITRATE": "Hit Rate",
             "num_searches": "Number of Searches",
             "District": "District"
             },)
    fig.update_layout(hovermode='closest')

    return fig


def create_racescatter(dff, title):
    color = {"White": '#1f77b4',
    "Black or African American":'#ff7f0e',
    "American Indian or Alaska Native":'#2ca02c',
    "Hispanic or Latino":'#d62728',
    "Asian":'#9467bd',
    "Native Hawaiian or Other Pacific Islander":'#17becf'}
    fig = px.scatter(dff, x='HITRATE', y='num_searches', color="DRRACE", facet_col='YEAR', title=title,
    labels={ "HITRATE": "Hit Rate",
             "num_searches": "Number of Searches",
             "DRRACE": "Race",
             "YEAR": "Year"
             },color_discrete_map=color)
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=-0.45))

    return fig


@app.callback(
    Output('race-scatter', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'))
def update_race_scatter(hoverData):
    beat_name = hoverData['points'][0]['customdata'][0]
    dff = grouped[grouped['Beat'] == beat_name]
    title = 'Beat Number: <b>{}</b>'.format(beat_name)
    return create_racescatter(dff,title)


@app.callback(
    Output('race-scatter-dist', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'))
def update_race_scatter_dist(hoverData):
    dist_name = hoverData['points'][0]['customdata'][2]
    dff = grouped[grouped['District'] == dist_name]
    title = 'District Number: <b>{}</b>'.format(dist_name)
    return create_racescatter(dff,title)

#token = open(".mapbox_token").read() # you will need your own token


def display_choropleth(df, title):
    fig = px.choropleth(
        df, geojson=gj, color="ColorBeat",
        locations="Beat", featureidkey="properties.beat_num",
        labels={"ColorBeat": ""},title=title)
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

@app.callback(
    Output("map", "figure"), 
    Input("crossfilter-indicator-scatter", "hoverData"))
def update_choropleth(hoverData):
    beat_name = hoverData['points'][0]['customdata'][0]
    district_name = hoverData['points'][0]['customdata'][2]
    df = grouped_norace[grouped_norace['YEAR'] == 2021]
    df.loc[:,'ColorBeat'] = "Chicago, IL"
    df.loc[(df['District'] == district_name),'ColorBeat'] = 'District: <b>{}</b>'.format(district_name)
    df.loc[(df['Beat'] == beat_name),'ColorBeat'] = 'Beat: <b>{}</b>'.format(beat_name)
    title = 'Map of Chicago, IL Police Beats'.format(district_name, beat_name)

    return display_choropleth(df, title)

