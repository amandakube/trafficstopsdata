from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

grouped = pd.read_csv('https://github.com/amandakube/trafficstopsdata/blob/eb589cff0cb99bbd797e69929c40d00330845a74/groupeddata.csv?raw=true')
grouped_norace = pd.read_csv('https://github.com/amandakube/trafficstopsdata/blob/eb589cff0cb99bbd797e69929c40d00330845a74/groupeddata_norace.csv?raw=true')
grouped["Beat"] = grouped["BEAT_I"].astype(str)
grouped_norace["Beat"] = grouped_norace["BEAT_I"].astype(str)
grouped["District"] = grouped["District"].astype(str)
grouped_norace["District"] = grouped_norace["District"].astype(str)


app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': '122'},{'customdata': '01'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='race-scatter'),
    ], style={'display': 'inline-block', 'width': '49%'}),
html.Div([
    html.Div(dcc.Slider(
        grouped_norace['YEAR'].min(),
        grouped_norace['YEAR'].max(),
        step=None,
        id='crossfilter-year--slider',
        value=grouped_norace['YEAR'].max(),
        marks={str(year): str(year) for year in grouped_norace['YEAR'].unique()}
    ), style={'width': '49%', 'display': 'inline-block', 'padding-bottom':'25%'}),
    html.Div([
        dcc.Graph(id='race-scatter-dist'),
    ], style={'display': 'inline-block', 'width': '49%'}),
]) 
])


@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('crossfilter-year--slider', 'value'))
def update_graph(year_value):
    dat = grouped_norace[grouped_norace['YEAR'] == year_value]
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


if __name__ == '__main__':
    app.run_server(threaded=True)
