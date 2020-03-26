#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 02 10:13:22 2019

@author: ivancalderon
"""
# %%
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
import get_data as gt
import plotly.graph_objs as go
import pandas as pd
import datetime as dt
import json
import numpy as np


# %%
app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1('Stock Price Statistics', className='title'),
    html.Div(className='mini-container',
            children=[
                    dcc.Input(
                                placeholder='Enter a Stock ticker...',
                                id='ticker_dropdown',
                                type='text',
                                value='x',
                                style={'width': '300px'}
                                 ),
                    html.H3('number', id='last_price')
                     ]
             ),
    html.Div(className='grid-container',
             children=[
             dcc.Graph(
                id='expec_by_hour',
                className='item1',
                config={'displayModeBar': False}
                ),
             dcc.Graph(
                id='highs_1st_hour',
                className='item2',
                config={'displayModeBar': False}
            ),
             dcc.Graph(
                id='lows_1st_hour',
                className='item3',
                config={'displayModeBar': False}
            ),
             dcc.Graph(
                id='day_of_week',
                className='item4',
                config={'displayModeBar': False}
            ),
            dcc.Graph(
                id='volume_dist',
                className='item6',
                config={'displayModeBar': False}
            ),
            dcc.Graph(
                id='daily_range',
                className='item5',
                config={'displayModeBar': False}
            ),
            dcc.Graph(
                id='tvol',
                className='item7',
                config={'displayModeBar': False}
            ),
            html.Div(
                id="data_store",
                style={'display': 'none'}
            )
             ])
    ])

@app.callback(
    Output('data_store', 'children'), 
    [Input('ticker_dropdown', 'value')]
    )
def clean_data(value):
   start = dt.datetime.now()
   futures =  gt.task_manager(value)
   intraday = futures['intraday'].result()
   daily = futures['daily'].result()
   data_dict = {"intraday": intraday.to_json(),
            "daily": daily.to_json()}
   print(dt.datetime.now() - start)
   return json.dumps(data_dict)


@app.callback(
    Output('last_price', 'children'), 
    [Input('data_store', 'children')]
    )
def get_last_price(data_dict):
    data = json.loads(data_dict)
    values = pd.read_json(data['intraday'])
    o = float(values['Open'].tail(1))
    h = float(values['High'].tail(1))
    l = float(values['Low'].tail(1))
    c = float(values['Close'].tail(1))
    v = float(values['Volume'].tail(1))/1000000
    nice = f"Last Print... Open: ${o:,.2f}, High: ${h:,.2f}, Low: ${l:,.2f}, Close: ${c:,.2f}, Volume: {v:,.2f}"
    return nice



@app.callback(
    Output('expec_by_hour', 'figure'), 
    [Input('data_store', 'children')]
    )
def update_expec_hour(data_dict):
    data = json.loads(data_dict)
    values = gt.expected_move(pd.read_json(data['intraday']), 'intraday')
    points = [('9:30', '9:45'), ('9:45', '10:00'), ('10:00', '10:15'), ('10:15', '10:30')]
    traces = []
    for point in points:
        start, end = point
        df = values.between_time(start, end, include_start=False)
        traces.append(go.Box(y=df['Range'],
                             showlegend=False,
                             name=end)
                      )
    return {
        'data': traces,
        'layout': go.Layout(title='Expected move each 15 min',
                            legend=None,
                            autosize=False,
                            margin={'l': 30, 'r': 5, 't': 65, 'b': 40},
                            #height=250,
                            #width=300
                            )
    }


@app.callback(
    [Output('highs_1st_hour', 'figure'),
     Output('lows_1st_hour', 'figure'),
     Output('tvol', 'figure')], 
    [Input('data_store', 'children')]
    )
def update_peaks(data_dict):
    data = json.loads(data_dict)
    intraday = pd.read_json(data['intraday'])
    h, l = gt.first_hour_peak(intraday)
    y = intraday.groupby(pd.Grouper(freq="B"))
    traces = []
    for day in y:
        df = day[1].copy()
        df.loc[:, 'volcumsum'] = (df.loc[:, 'Volume']
                                    .cumsum()
                                    .shift(1))
        traces.append(go.Bar(x=df.index, y=df['Volume'],
                base=df['volcumsum'],
                marker_color='blue',
                showlegend=False
                ))
    tvol = {'data': traces[-7:],
            'layout': go.Layout(
                                title='Total Volume each 15 min',
                                xaxis={'type': 'category',
                                       #'nticks': 7,
                                       'tickangle': -45,
                                       'tickformat': '%d-%m',
                                       #'tickmode': 'auto',
                                       'tickvals': [],
                                       'ticktext': []
                                       }
                                    
            ) }
    h_figure = {'data': [go.Bar(y=h, marker={'color': 'blue'})],
                'layout': go.Layout(
                    title='% times that Highs occured in interval',
                    legend=None,
                    margin={'l': 30, 'r': 5, 't': 65, 'b': 40},
                    xaxis={
                        'ticktext': ['15min', '30min', '1h'],
                        'tickvals': list(range(3))
                    },
                    yaxis={'range': (0, 100)},
                    #height=250,
                    #width=300
                )}
    l_figure = {'data': [go.Bar(y=l, marker={'color': 'orange'})],
                'layout': go.Layout(
                    title='% times that Lows occured in interval',
                    legend=None,
                    margin={'l': 30, 'r': 5, 't': 65, 'b': 40},
                    xaxis={
                        'ticktext': ['15min', '30min', '1h'],
                        'tickvals': list(range(3))
                    },
                    yaxis={'range': (0, 100)},
                    #height=250,
                    #width=300
                )}
    return h_figure, l_figure, tvol


@app.callback(
    [Output('day_of_week', 'figure'),
     Output('daily_range', 'figure'),
     Output('volume_dist', 'figure')], 
    [Input('data_store', 'children')]
    )
def update_day_of_week(data_dict):
    data = json.loads(data_dict)
    values = gt.week_day_move(pd.read_json(data['daily']))
    traces = []
    vol_traces = []
    for x in values.keys():
        info = values[x]
        traces.append(go.Box(y=info['Range'],
                             name=x,
                             showlegend=False))
        vol_traces.append(go.Box(y=info['Volume'],
                             name=x,
                             showlegend=False))
    day_spread = {'data': traces,
           'layout': go.Layout(
                                title='Range spread per day of the week',
                                #height=250,
                                #width=450
                                )
           }
    vol_dist = {'data': vol_traces,
           'layout': go.Layout(
                                title='Volume spread per day of the week',
                                #height=250,
                                #width=450
                                )
           }
    df = pd.read_json(data['daily'])
    df.loc[:, 'sign'] = np.where(df['Close'] > df['Open'], 1, -1)
    df.loc[:, 'Range2'] = (df['High'] - df['Low']) * df['sign']
    colors = ["green" if x > 0 else "red" for x in df['Range2'].tail(30).values]
    dates = [dt.datetime.strftime(x, "%d-%m") for x in df['Range2'].tail(30).index]
    day_range = {'data': [go.Bar(y=df["Range2"].tail(30), marker={'color': colors})],
            'layout': go.Layout(
                                title='Range of Stock in last 30 days',
                                xaxis={
                                'ticktext': dates,
                                'tickvals': list(range(len(df['Range2'].tail(30)))),
                                'tickfont': {'size': 14}},
                                #height=250,
                                #width=900
                                )
            }
    return day_spread, day_range, vol_dist

# %%
if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
