import pandas as pd
import numpy as np
import regex as re 

import requests
import json

import folium

import datetime as dt
from collections import Counter

import plotly.express as px

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
                external_stylesheets=[dbc.themes.FLATLY], # https://www.bootstrapcdn.com/bootswatch/   https://hackerthemes.com/bootstrap-cheatsheet/
                meta_tags=[{'name': 'viewport',                                   # meta_tag allows responsiveness for mobile browsing
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

app.title = "Travaux ville de Bordeaux"

server = app.server

app.layout = html.Div([
    dbc.Row(
        dbc.Col(html.H1("Travaux de la ville de Bordeaux",
                        className='text-center text-primary mb-4'),
                width=12)
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
        return dbc.Row([
                        dbc.Col([
                            dcc.Graph(
                                id='graph_1',
                                figure = duree_travaux()),
                                
                        ],style={
                                #'width': '200px',
                                'margin-top': 15,
                                'margin-left': 5,
                                },
                        #className="float-left"
                        # width={'size':5, 'offset':1, 'order':1},
                       # xs=12, sm=12, md=12, lg=5, xl=5
                        ),
                        dbc.Col([
                            dcc.Graph(
                                id='graph_2',
                                figure = type_travaux_frequence()),
                        ],style={
                                #'width': '200px',
                                'margin-top': 15,
                                'margin-left': 5,
                                },
                       # className="float-right"#"align-middle"
                        # width={'size':5, 'offset':1, 'order':1},
                        #xs=12, sm=12, md=12, lg=5, xl=5
                        ),
                        ])

    elif tab == 'tab_2_map':

        point = [44.837789, -0.57918]

        m = folium.Map(
                    location=point,
                    t=7, 
                    zoom_start=14
                    )

        for _libelle, _localisation, _coordinates, _debut, _fin, _address in zip(complete_df['libelle_split'], complete_df['localisation_split'], complete_df['geolocalisation'], complete_df['fields.date_debut'].dt.strftime('%d/%m'), complete_df['fields.date_fin'].dt.strftime('%d/%m'), complete_df["address"]):
            
            if type(_libelle) != list:
                _libelle = _libelle[2:-2].split(',')[0]
                _libelle = _libelle.replace("'", "")

            if type(_localisation) != list:
                _localisation = _localisation[2:-2].split(',')#[0]
           # _debut = _debut.dt.strftime('%Y-%m-%d')
            #_fin = _fin.dt.strftime('%Y-%m-%d')
            try:
                _coordinates = [float(i) for i in _coordinates[1:-1].split(', ')]
                print(type(_coordinates), _coordinates)
            except:
                _coordinates = np.NaN

            if type(_coordinates) == list:
                folium.Marker(
                            location = _coordinates, 
                            popup = f"{_address}.\n{_libelle}.\ndu {_debut} jusqu'au {_fin}"
                            ).add_to(m)

        m.save("mymapnew.html")

        return html.Div([html.Iframe(id='map', srcDoc=open('mymapnew.html', 'r').read(), width='100%', height='600')],                 
                        style={
                               #'width': '200px',
                               'margin-top': 15,
                               })
 
    elif tab == 'a_propos':

        return dbc.Row([dcc.Markdown("""
                #### À propos du site
                Site conçu sous licence ouverte par [Benjamin Baret](https://www.linkedin.com/in/benjamin-baret-6957471bb), Data Analyst/Scientist        
                Données publiques de la ville de Bordeaux consultables à ce [lien](https://opendata.bordeaux-metropole.fr/explore/dataset/ci_acte_a/information/)     
                Site réalisé grâce à [Dash](https://plotly.com/dash/), code disponible [ici](https://github.com/WildBenji/travaux_bordeaux)
                """)], justify="center", align="center", className="text-center", style={'margin-top': 15})

if __name__ == '__main__':
    app.run_server(debug=True)




