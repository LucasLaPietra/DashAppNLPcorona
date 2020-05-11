# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 19:08:59 2020

@author: Lucas E. La Pietra
Changes: implementado filtro por fechas
"""

import pandas as pd
import nltk
import plotly.express as px
import string
import dash
from datetime import datetime as dt
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from plotly.graph_objs import *
import re


def generarstopwords():
    stopwords = nltk.corpus.stopwords.words('spanish') + list(string.punctuation)
    stopwords.extend(['“', '”', '``', "''"])
    return stopwords


def generardffrec(corpus):
    stopwords = generarstopwords()
    freqdist = nltk.FreqDist(w.lower() for w in corpus if w.lower() not in stopwords)
    dffreq = pd.DataFrame(freqdist.items(), columns=['Palabra', 'Frecuencia'])
    return dffreq


def transformdf(df, fechai, fechaf):
    mask = (df['Fecha'] >= fechai) & (df['Fecha'] <= fechaf)
    df = df.loc[mask]
    df = df[['Corpus', 'Diario', 'Categoria']]
    df['Corpus'] = df['Corpus'].astype(str)
    aggregation_functions = {'Corpus': (' '.join)}
    df_new = df.groupby(['Diario', 'Categoria'], as_index=False).aggregate(aggregation_functions)
    return df_new


cantpalabras = 25
dforig = pd.read_excel('https://github.com/luxlp/NoticiasScrapeadas/blob/master/BDNoticias-Abril.xlsx?raw=true')
df = transformdf(dforig, '25/04/2020', '30/04/2020')

dfclarin = df[df['Diario'] == 'Clarin']
catclarin = list(dfclarin['Categoria'])
dflanacion = df[df['Diario'] == 'La Nacion']
catlanacion = list(dflanacion['Categoria'])
dfinfobae = df[df['Diario'] == 'Infobae']
catinfobae = list(dfinfobae['Categoria'])
categorias = catinfobae
words = nltk.tokenize.word_tokenize(df['Corpus'].iloc[0])
dffreq = generardffrec(words)
layout = Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#2e2e2e',
    colorscale=dict(sequential=px.colors.sequential.Tealgrn_r),
    font=dict(
        family="Open Sans",
        size=12,
        color="#d8d8d8"
    )
)
fig = px.bar(dffreq.nlargest(cantpalabras, columns=['Frecuencia']), x='Palabra', y='Frecuencia', color='Frecuencia')
fig.layout = layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash()
server = app.server

app.layout = html.Div(children=[
    # fila titulo
    html.Div(children=[
        html.Div(children=[
            html.H1(children='Frecuencia de palabras en las noticias sobre Coronavirus'),
            html.H5(children='Por Lucas La Pietra')], className='ten columns'),
        html.Div(children=[
            html.Img(className="logo", src=app.get_asset_url("LogoUTN2.png"))], className='div-for-logo'
        )
    ], className='one row'),
    html.Div(children=[
        dcc.Graph(id='barchart', figure=fig)], className='six rows'),
    # fila dropdowns
    html.Div(children=[
        html.Div(children=[
            html.Label('Seleccionar diario:'),
            dcc.Dropdown(
                id='DiarioDropdown',
                options=[
                    {'label': 'Infobae', 'value': 'Infobae'},
                    {'label': 'La Nacion', 'value': 'La Nacion'},
                    {'label': 'Clarin', 'value': 'Clarin'}
                ],
                value='Infobae',
                clearable=False,
            )], className='six columns'),
        html.Div(children=[
            html.Label('Seleccionar categoria:'),
            dcc.Dropdown(
                id="CatDropdown",
                options=[{'label': categoria, 'value': categoria} for categoria in categorias],
                value=categorias[0],
                clearable=False,
            )], className='six columns')
    ], className="div-user-controls one row"),
    # fila date
    html.Div(children=[
        html.Label('Rango de fechas:'),
        dcc.DatePickerRange(
            id='daterange',
            min_date_allowed=dt(2020, 4, 25),
            max_date_allowed=dt(2020, 4, 30),
            start_date=dt(2020, 4, 25).date(),
            end_date=dt(2020, 4, 30).date(),
            display_format='D/M/Y',
            calendar_orientation='horizontal')
    ], className="one row div-datepick"),
    # fila slider
    html.Div(children=[
        html.Label('Cantidad de palabras a mostrar:'),
        dcc.Slider(
            id='slider',
            min=10,
            max=50,
            marks={10: '10',
                   20: '20',
                   30: '30',
                   40: '40',
                   50: '50'},
            value=25)
    ], className="one row div-slider")
])


@app.callback(Output('barchart', 'figure'),
              [Input('slider', 'value'), Input('DiarioDropdown', 'value'), Input('CatDropdown', 'value')
                  , Input('daterange', 'start_date'), Input('daterange', 'end_date')]
              )
def update_figure(rango, diario, categoria, fechai, fechaf):
    fechai = dt.strptime(re.split('T| ', fechai)[0], '%Y-%m-%d')
    fechai_string = fechai.strftime('%d/%m/%Y')
    fechaf = dt.strptime(re.split('T| ', fechaf)[0], '%Y-%m-%d')
    fechaf_string = fechaf.strftime('%d/%m/%Y')
    df = transformdf(dforig, fechai_string, fechaf_string)
    dfclarin = df[df['Diario'] == 'Clarin']
    dflanacion = df[df['Diario'] == 'La Nacion']
    dfinfobae = df[df['Diario'] == 'Infobae']
    if diario == 'Clarin':
        noticia = dfclarin[dfclarin['Categoria'] == categoria]
    if diario == 'Infobae':
        noticia = dfinfobae[dfinfobae['Categoria'] == categoria]
    if diario == 'La Nacion':
        noticia = dflanacion[dflanacion['Categoria'] == categoria]
    words = nltk.tokenize.word_tokenize(noticia['Corpus'].iloc[0])
    dffreq = generardffrec(words)
    fig = px.bar(dffreq.nlargest(rango, columns=['Frecuencia']), x='Palabra', y='Frecuencia', color='Frecuencia')
    fig.layout = layout
    return fig


@app.callback(
    [Output("CatDropdown", "options"), Output("CatDropdown", "value")],
    [Input("DiarioDropdown", "value"), Input('daterange', 'start_date'), Input('daterange', 'end_date')],
)
def update_options(value, fechai, fechaf):
    fechai = dt.strptime(re.split('T| ', fechai)[0], '%Y-%m-%d')
    fechai_string = fechai.strftime('%d/%m/%Y')
    fechaf = dt.strptime(re.split('T| ', fechaf)[0], '%Y-%m-%d')
    fechaf_string = fechaf.strftime('%d/%m/%Y')
    df = transformdf(dforig, fechai_string, fechaf_string)
    dfclarin = df[df['Diario'] == 'Clarin']
    catclarin = list(dfclarin['Categoria'])
    dflanacion = df[df['Diario'] == 'La Nacion']
    catlanacion = list(dflanacion['Categoria'])
    dfinfobae = df[df['Diario'] == 'Infobae']
    catinfobae = list(dfinfobae['Categoria'])
    if value == 'Clarin':
        return [{'label': categoria, 'value': categoria} for categoria in catclarin], catclarin[0]
    if value == 'Infobae':
        return [{'label': categoria, 'value': categoria} for categoria in catinfobae], catinfobae[0]
    if value == 'La Nacion':
        return [{'label': categoria, 'value': categoria} for categoria in catlanacion], catlanacion[0]


app.run_server(debug=True, use_reloader=False)
