import pandas as pd
import numpy as np
import regex as re 

import requests
import json

import folium

import datetime as dt
from collections import Counter

import plotly.express as px


####################################################################################


def address_cleaner(_list : list):

    _whitelist = ['rue', 'avenue', 'boulevard', 'impasse', 'quai', 'pont', 'quartier', 'Centre', 'ville', 'centre']

    for _address in _list:
        _index = _list.index(_address)
        _res = []
        for w in _address.split():
            if w[0].isupper() or w.isnumeric() or w in _whitelist:
                _res.append(w)
        _list[_index] = " ".join(_res)

    return _list


def geolocator(_address : str):

    _address = _address.replace(' ', '+') + "+Bordeaux+France"

    gouv_data_api =   f"https://api-adresse.data.gouv.fr/search/?q={_address}" 

    resp = requests.get(gouv_data_api)
    resp_dic = json.loads(resp.text)

    try:
        _latitude = resp_dic["features"][0]['geometry']['coordinates'][0]
        _longitude = resp_dic["features"][0]['geometry']['coordinates'][1]
        _address = resp_dic["features"][0]['properties']['label'][:-15]

        return [_longitude, _latitude], _address
    except:
        pass


####################################################################################


saved_dataset = pd.read_csv('https://raw.githubusercontent.com/WildBenji/travaux_bordeaux/main/dataset.csv', encoding='utf-8') # pd.read_csv('dataset copy.csv', encoding='utf-8') #

check_dataset = saved_dataset[['record_timestamp', 'fields.gid_emprise', 'fields.libelle', 'fields.type_emprise',
'fields.date_debut','fields.date_fin', 'fields.gid_acte', 'fields.rs_chantier', 'fields.localisation_emprise', 
'fields.gml_id', 'fields.gid', 'fields.numero_acte']]

_link = """https://opendata.bordeaux-metropole.fr/api/records/1.0/search/?dataset=ci_acte_a&q=date_debut%3E%3D%222021-01-01%22&q=date_fin%3C%3D%222021-12-31%22
&rows=10000"""

resp = requests.get(_link)

resp_data = pd.json_normalize(resp.json(), record_path=['records'])

df_full = resp_data[['record_timestamp', 'fields.gid_emprise', 'fields.libelle', 'fields.type_emprise',
'fields.date_debut','fields.date_fin', 'fields.gid_acte', 'fields.rs_chantier', 'fields.localisation_emprise', 
'fields.gml_id', 'fields.gid', 'fields.numero_acte']]

df_nan = df_full[df_full.isna().any(axis=1)]
df = df_full.dropna()

print(f"Taille originale du fichier : {saved_dataset.shape}\nTaille du fichier json sans NaN : {df.shape}")

missing_data = df[~df['fields.gid_acte'].isin(check_dataset['fields.gid_acte'])]
missing_data.dropna(inplace=True)

if missing_data.empty == False:

    print(f"Nombre de nouvelles lignes détectées : {missing_data.shape}")

   # temp_libelle = missing_data['fields.libelle'].str.get_dummies(sep="/")
   # temp_type_emprise = missing_data['fields.type_emprise'].str.get_dummies(sep="/")

   #missing_data = missing_data.join(temp_libelle)

    missing_data['libelle_split'] = missing_data['fields.libelle'].str.split('/')
    missing_data['localisation_split'] = missing_data['fields.localisation_emprise'].str.split('/')
    missing_data['type_emprise_split'] = missing_data['fields.type_emprise'].str.split('/')

    missing_data['localisation_split'] = missing_data['localisation_split'].apply(lambda x : address_cleaner(x))

    missing_data['geolocalisation'] = ""

    for i in range(len(missing_data)):

        _coor = missing_data['localisation_split'].iloc[i][0].split(',')[0]
        missing_data['geolocalisation'].iloc[i], missing_data['address'].iloc[i] = geolocator(_coor)

    complete_df = pd.concat([saved_dataset, missing_data], axis=0, ignore_index=True).fillna(0)

    print(f"Taille du nouveau fichier : {complete_df.shape}")

else:
    complete_df = saved_dataset
    print("Pas de nouvelles données")

complete_df['fields.date_fin'] = pd.to_datetime(complete_df['fields.date_fin'])
complete_df['fields.date_debut'] = pd.to_datetime(complete_df['fields.date_debut'])
complete_df['temps_travaux'] = complete_df['fields.date_fin'] - complete_df['fields.date_debut'] + dt.timedelta(days=1)

    
temp_libelle = complete_df['fields.libelle'].str.get_dummies(sep="/")
temp_type_emprise = complete_df['fields.type_emprise'].str.get_dummies(sep="/")

complete_df.dropna(subset=['geolocalisation'], inplace=True)

def get_df():

    return complete_df


####################################################################################


def graph_type_emprise():

    type_emprise = pd.DataFrame(temp_type_emprise.value_counts(), columns=['count'])
    return type_emprise

possible_works_list = []

for i in complete_df['fields.libelle'].unique():
    for e in i.split('/'):
        if e not in possible_works_list:
            possible_works_list.append(e)


all_libelle = []

for i in complete_df['fields.libelle']:
    for e in i.split('/'):
        for a in e.split(';'):
            all_libelle.append(a)


####################################################################################


all_libelle_count_dic = dict(Counter(all_libelle)) 

all_libelle_count = pd.DataFrame.from_dict(all_libelle_count_dic, orient='index', columns=['count'])
all_libelle_count = all_libelle_count.sort_values(by='count', ascending=False)


def type_travaux_frequence():

    fig = px.histogram(all_libelle_count, x="count", y=all_libelle_count.index)

    fig.update_layout(paper_bgcolor="darkgray", title="Types d'emprise et leur fréquence", title_x=0.5)

    fig.update_xaxes(title="")
    fig.update_yaxes(title="", autorange='reversed')
    fig.update_traces(hovertemplate="Total <i> '%{y}' </i> = %{x}")

    return fig 


####################################################################################

_duration = complete_df[['fields.gid_emprise', 'temps_travaux']]

_duration['temps_travaux'] = _duration['temps_travaux'].astype('str').apply(lambda x : x[:-23])
_duration['temps_travaux'] = _duration['temps_travaux'].astype('int')


def duree_travaux():

    fig = px.box(_duration, y="temps_travaux", points="all")
    fig.update_layout(paper_bgcolor="darkgray", title="Répartition de la durée des chantiers", title_x=0.5)
    fig.update_yaxes(title="Jours de travaux")

    return fig

"""
_length = complete_df[['fields.gid_emprise', 'temps_travaux']].groupby(by='temps_travaux').count().reset_index()
_length.rename(columns={'fields.gid_emprise' : 'count'}, inplace=True)
_length.sort_values(by='temps_travaux', ascending=True, inplace=True)
_length['temps_travaux'] = _length['temps_travaux'].astype('str')
try:
    _length['temps_travaux'] = _length['temps_travaux'].apply(lambda x : x[:-5]) # [:-23]
    _length['total'] = _length['temps_travaux'].astype('int') * _length['count'] 
except:
    pass


def duree_travaux():

   # _length['temps_travaux'] = _length['temps_travaux'].astype('str')
    #_length['temps_travaux'] = _length['temps_travaux'].apply(lambda x : x[:-5]) # [:-23]
    fig = px.histogram(_length, x="count", y='temps_travaux', nbins=20)
    print(_length.dtypes)
    fig.update_layout(paper_bgcolor="darkgray", title="Nombre de chantiers pour une durée donnée", title_x=0.5)

    fig.update_xaxes(title="Total travaux")
    fig.update_yaxes(title="Jours de travaux")
    fig.update_traces(hovertemplate="Total <i> %{y} jours </i> = %{x} travaux")
    fig.update_layout(bargap=0.2,
                      yaxis=dict(tickformat="%d"))

    return fig

"""



