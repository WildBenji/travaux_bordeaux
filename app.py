import pandas as pd
import numpy as np
import regex as re 

import requests
import json

import folium

import datetime as dt
from collections import Counter

import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components import Div 

from data_manip import type_travaux_frequence, graph_type_emprise, duree_travaux, complete_df, address_cleaner, geolocator


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
                __name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP]# external_stylesheets
                )

app.title = "Travaux ville de Bordeaux"

server = app.server

app.layout = html.Div([
    html.H3(
    id='Main title',
    children='Travaux de la ville de Bordeaux',
    style={'text-align':'center'}
    ),
    #html.H1('Dash Tabs component demo'),
    dcc.Tabs(id="3_tabs", value='tab_1_graph', children=[
        dcc.Tab(label='Graphiques', value='tab_1_graph'),
        dcc.Tab(label='Carte', value='tab_2_map'),
        dcc.Tab(label='À Propos', value='a_propos'),
    ]),
    html.Div(id='tabs_content')
])

@app.callback(Output('tabs_content', 'children'),
              Input('3_tabs', 'value'))

def render_content(tab):
    
    if tab == 'tab_1_graph':
        numdate = [x for x in range(len(complete_df['fields.date_fin'].unique()))]
        return html.Div([
            html.H5(
                    'Distribution temps des travaux',
                    style={'text-align':'center'}
                    ),
            dcc.Slider(min=numdate[0], #the first date
               max=numdate[-1], #the last date
               value=numdate[0], #default: the first
               marks = {numd:date.strftime('%d/%m') for numd,date in zip(numdate, complete_df['fields.date_fin'].dt.date.unique())}
               ),
            dcc.Graph(
                id='graph_1',
                figure = duree_travaux()),
            dcc.Graph(
                id='graph_2',
                figure = type_travaux_frequence()),
                                
                ])


    elif tab == 'tab_2_map':

        point = [44.837789, -0.57918]

        m = folium.Map(
                    location=point,
                    t=7, 
                    zoom_start=14
                    )

        for _libelle, _localisation, _coordinates in zip(complete_df['libelle_split'], complete_df['localisation_split'], complete_df['geolocalisation']):
            
            _libelle = _libelle[0]
            _localisation = _localisation[0]
            _coordinates = [float(i) for i in _coordinates[1:-1].split(', ')]
            print(type(_coordinates), _coordinates)

            if _coordinates:
                folium.Marker(location = _coordinates, 
                            popup = f"{_libelle}." # \n {(' '.join(adr.split()[:-4])[:-1])}"
                            ).add_to(m)

        m.save("mymapnew.html")

        return html.Div([
                         html.Iframe(id='map', srcDoc=open('mymapnew.html', 'r').read(), width='100%', height='600')                         
                         ])
 
    elif tab == 'a_propos':

        return html.Div([dcc.Markdown("""
                ## À propos du site
                Site conçu sous licence ouverte par [Benjamin Baret](https://www.linkedin.com/in/benjamin-baret-6957471bb), Data Analyst/Scientist        
                Données publiques de la ville de Bordeaux consultables à ce [lien](https://opendata.bordeaux-metropole.fr/explore/dataset/ci_acte_a/information/)     
                Site réalisé grâce à [Dash](https://plotly.com/dash/), code disponible [ici](https://github.com/WildBenji/travaux_bordeaux)
                """)])

if __name__ == '__main__':
    app.run_server(debug=True)




