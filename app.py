# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 19:08:59 2020

@author: Lucas E. La Pietra
Changes: Añadido titulo y favicon
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
import time


def generarstopwords():
    stopwords = nltk.corpus.stopwords.words('spanish') + list(string.punctuation)
    stopwords.extend(['“', '”', '``', "''"])
    return stopwords


def generardffreccorpus(corpus):
    stopwords = generarstopwords()
    freqdist = nltk.FreqDist(w for w in corpus if w.lower() not in stopwords)
    dffreqcorpus = pd.DataFrame(freqdist.items(), columns=['Palabra', 'Frecuencia'])
    return dffreqcorpus


def addtrigrams(dffreq):
    listatuplas = []
    for i in range(len(dffreq)):
        for j in range(len(dffreq)):
            if (dffreq.iloc[i]['Palabra'][1] == dffreq.iloc[j]['Palabra'][0]) and (
                    dffreq.iloc[i]['Frecuencia'] == dffreq.iloc[j]['Frecuencia']):
                trigram = dffreq.iloc[i]['Palabra'] + ((dffreq.iloc[j]['Palabra'][1]),)
                dffreq.at[i, 'Palabra'] = trigram
                listatuplas.append(dffreq.iloc[j]['Palabra'])
    for tupla in listatuplas:
        dffreq = dffreq[dffreq.Palabra != tupla]
    return dffreq


def generardffrecbgs(corpus):
    bgs = nltk.bigrams(corpus)
    stopwords = generarstopwords()
    freqdist = nltk.FreqDist(w for w in bgs if (w[0].lower() not in stopwords) and (w[1].lower() not in stopwords))
    dffreq = pd.DataFrame(freqdist.items(), columns=['Palabra', 'Frecuencia'])
    dffreq = dffreq[dffreq['Frecuencia'] > 1]
    dffreq = dffreq.reset_index(drop=True)
    dffreq = addtrigrams(dffreq)
    return dffreq


def generardffrec(corpus):
    listapalabras = []
    dffreq = generardffreccorpus(corpus)
    dffreq2 = generardffrecbgs(corpus)
    dffreq2 = dffreq2[dffreq2['Frecuencia'] > 1]
    for b in range(len(dffreq2)):
        freq = dffreq.iloc[b]['Frecuencia']
        for w in dffreq2.iloc[b]['Palabra']:
            if dffreq.iloc[b]['Frecuencia'] == freq:
                listapalabras.append(w)
    for palabra in listapalabras:
        dffreq = dffreq[dffreq.Palabra != palabra]
    dffreq2['Palabra'] = dffreq2['Palabra'].str.join(" ")
    dffreq = dffreq.append(dffreq2)
    dffreq = dffreq.reset_index(drop=True)
    return dffreq


def transformdf(df, fechai, fechaf):
    mask = (df['Fecha'] >= fechai) & (df['Fecha'] <= fechaf)
    df = df.loc[mask]
    df = df[['Corpus', 'Diario', 'Categoria']]
    df['Corpus'] = df['Corpus'].astype(str)
    aggregation_functions = {'Corpus': (' '.join)}
    df_new = df.groupby(['Diario', 'Categoria'], as_index=False).aggregate(aggregation_functions)
    return df_new


def dfrepeticiondiarios(df, fechai, fechaf):
    mask = (df['Fecha'] >= fechai) & (df['Fecha'] <= fechaf)
    df = df.loc[mask]
    df_new = df.groupby('Diario', as_index=False).size().reset_index(name='Count')
    return df_new


def dfrepeticioncategorias(df, fechai, fechaf):
    mask = (df['Fecha'] >= fechai) & (df['Fecha'] <= fechaf)
    df = df.loc[mask]
    df_new = df.groupby(['Diario', 'Categoria'], as_index=False).size().reset_index(name='Count')
    return df_new


def preparardfbigramas(df):
    df['Longitud'] = df['Palabra'].apply(len)
    df['Palabra'] = df['Palabra'].apply(str)
    return df


cantpalabras = 25
dforig = pd.read_excel('https://github.com/luxlp/NoticiasScrapeadas/blob/master/BDNoticias.xlsx?raw=true')
dftopic = pd.read_excel('https://github.com/luxlp/NoticiasScrapeadas/blob/master/BDTopicos.xlsx?raw=true')
dftopictable = dftopic[['Topico', 'Nombre_Topico', 'Keywords']]

dftopicclarin = dforig[dforig['Diario'] == 'Clarin']
dftopiclanacion = dforig[dforig['Diario'] == 'Clarin']
dftopicinfobae = dforig[dforig['Diario'] == 'Clarin']

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
    ),
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=30,
        pad=4
    ),
)
topicpie = px.pie(dftopic, names='Topico', values='Num_Documentos', color='Num_Documentos',
                  color_discrete_sequence=["#b0f2bc", "#73e0a8", "#39b3a3", "#257d98"])
topicpie.layout = layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = 'NLP-Noticias Corona'
server = app.server

BarraSuperior = dbc.Navbar(
    children=[
        html.Div(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col([
                        html.A(html.Img(className="logo", src=app.get_asset_url("LogoUTN.png")),
                               href='http://www.frcu.utn.edu.ar/')
                    ], md=3),
                    dbc.Col([
                        html.H1(children='Frecuencia de palabras en las noticias sobre Coronavirus'),
                        html.A(html.H5(children='Por Lucas La Pietra'),href='https://www.linkedin.com/in/lucas-la-pietra-0b1ab6194/')
                    ])
                ],
                align="center",
                no_gutters=True
            )
        )
    ],
    color="dark",
    dark=True,
    sticky="top"
)

SeleccionFecha = [
    dbc.CardHeader(html.H5("Numero de noticias a analizar")),
    dbc.CardBody(
        [
            dbc.Row(
                dbc.Col([
                    html.H2(children='Rango de fechas a analizar:'),
                    dcc.DatePickerRange(
                        id='daterange',
                        min_date_allowed=dt(2020, 5, 1),
                        max_date_allowed=dt(2020, 5, 31),
                        start_date=dt(2020, 5, 1).date(),
                        end_date=dt(2020, 5, 31).date(),
                        display_format='D/M/Y',
                        calendar_orientation='horizontal'),
                    html.H3(id='totalNoticias', className='totalNoticias')
                ], width=6, className='daterow'

                ), justify="center"
            ),
            dbc.Spinner(size="lg",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col([
                                        dbc.Jumbotron([
                                            html.H5(children='Distribucion de noticias por diario'),
                                            dcc.Graph(id='figrepeticiondiarios', style={"padding-top": 50})
                                        ])
                                    ]
                                        , md=6
                                    ),
                                    dbc.Col(
                                        dbc.Jumbotron([
                                            html.H5(children='Cantidad de noticias por categoria para el diario:'),
                                            dcc.Dropdown(
                                                id='diarioDropdownRep',
                                                options=[
                                                    {'label': 'Infobae', 'value': 'Infobae'},
                                                    {'label': 'La Nacion', 'value': 'La Nacion'},
                                                    {'label': 'Clarin', 'value': 'Clarin'}
                                                ],
                                                value='Infobae',
                                                clearable=False),
                                            dcc.Graph(id='figrepeticioncategoria')
                                        ]), md=6
                                    )
                                ], style={"padding-top": 10}),
                        ])
        ])
]

FreqHistGraph = [
    dbc.CardHeader(html.H5("Analisis de frecuencia")),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col([
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
                        )], md=6
                    ),
                    dbc.Col([
                        html.Label('Seleccionar categoria:'),
                        dcc.Dropdown(
                            id="CatDropdown",
                            options=[{'label': categoria, 'value': categoria} for categoria in categorias],
                            value=categorias[0],
                            clearable=False,
                        )], md=6
                    )
                ]),
            dbc.Row(
                dbc.Col([
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
                        value=25)], md=12
                ), style={"padding-top": 10}
            ),
            dbc.Spinner(size="lg",
                        children=[
                            dbc.Row(
                                dbc.Col(
                                    [
                                        dbc.Jumbotron([
                                            html.H5(children='Distribucion de frecuencia de palabras'),
                                            dcc.Graph(id='barchart')
                                        ])
                                    ]
                                    , md=12)
                            ),
                            dbc.Row(
                                dbc.Col(
                                    [
                                        dbc.Jumbotron([
                                            html.H5(children='N-gramas destacables'),
                                            dcc.Graph(id='ngramscatter')
                                        ])
                                    ]
                                    , md=12)
                            )
                        ])
        ])
]

AnalisisTopicos = [
    dbc.CardHeader(html.H5("Análisis de Topicos")),
    dbc.CardBody(
        [
            dbc.Row(
                dbc.Col([
                    html.H3(
                        children='A partir de un algoritmo LDA, se obtuvieron los siguientes 4 tópicos con una coherencia de 0.44'),
                ], width=6, className='daterow'

                ), justify="center"
            ),
            dbc.Row(
                [
                    dbc.Col([
                        dbc.Jumbotron([
                            html.H5(children='Distribucion de topicos en las noticias'),
                            dcc.Graph(id='figrepeticiontopicos',
                                      figure=topicpie,
                                      style={"padding-top": 50})
                        ])
                    ]
                        , md=6
                    ),
                    dbc.Col(
                        dbc.Jumbotron([
                            html.H5(children='Palabras clave por topico:'),
                            dbc.Table.from_dataframe(dftopictable, striped=True, dark=True, bordered=True, hover=True)
                        ]), md=6
                    )
                ], style={"padding-top": 10}),
            dbc.Row(
                dbc.Col([
                    html.H3(
                        children='Aporte de noticias hacia un topico'),
                ], width=6

                ), justify="center"
                , style={"padding-top": 40}),
            dbc.Row(
                [
                    dbc.Col([
                        html.H5('Seleccionar Topico:', style={"padding-top": 10}),
                        dcc.Dropdown(
                            id="TopicDropdown",
                            options=[{'label': topico, 'value': topico} for topico in dftopic['Nombre_Topico']],
                            value=dftopic['Nombre_Topico'][0],
                            clearable=False,
                        ),
                        html.H5('Seleccionar Diario:', style={"padding-top": 30}),
                        dcc.RadioItems(
                            id='TopicRadioButtons',
                            options=[
                                {'label': 'Todos', 'value': 'Todos'},
                                {'label': 'Infobae', 'value': 'Infobae'},
                                {'label': 'La Nacion', 'value': 'La Nacion'},
                                {'label': 'Clarin', 'value': 'Clarin'}
                            ],
                            value='Todos',
                            labelStyle={'display': 'block'}
                        )
                    ]
                        , md=3
                    ),

                    dbc.Col(
                        dbc.Jumbotron([
                            dbc.Spinner(size="lg",
                                        children=[
                                            dcc.Graph(id='topicscatter')]),
                            html.Label(
                                [
                                    '*El grafico muestra la colaboracion de cada noticia a su tópico preponderante, '
                                    'en cada noticia puede tratarse mas de un tópico.'])
                        ]), md=9
                    )

                ], style={"padding-top": 10})
        ])
]

BODY = dbc.Container(
    [
        dbc.Row([dbc.Col(dbc.Card(SeleccionFecha), className="w-100"), ], style={"marginTop": 30}),
        dbc.Row([dbc.Col(dbc.Card(FreqHistGraph)), ], style={"marginTop": 30}),
        dbc.Row([dbc.Col(dbc.Card(AnalisisTopicos)), ], style={"marginTop": 30}),
    ],
    className="mt-12",
)

app.layout = html.Div(children=[
    BarraSuperior,
    BODY])


@app.callback([Output('figrepeticiondiarios', 'figure'), Output('totalNoticias', 'children')],
              [Input('daterange', 'start_date'), Input('daterange', 'end_date')]
              )
def update_figure(fechai, fechaf):
    fechai = dt.strptime(re.split('T| ', fechai)[0], '%Y-%m-%d')
    fechai_string = fechai.strftime('%d/%m/%Y')
    fechaf = dt.strptime(re.split('T| ', fechaf)[0], '%Y-%m-%d')
    fechaf_string = fechaf.strftime('%d/%m/%Y')
    df = dfrepeticiondiarios(dforig, fechai_string, fechaf_string)
    numeronoticias = str(df.iloc[0]['Count'] + df.iloc[1]['Count'] + df.iloc[2]['Count'])
    frase = 'En total se analizaran ' + numeronoticias + ' noticias.'
    fig = px.pie(df, names='Diario', values='Count', color='Count',
                 color_discrete_sequence=["#257d98", "#51cba3", "#adf1ba"])
    fig.layout = layout
    return fig, frase


@app.callback(Output('figrepeticioncategoria', 'figure'),
              [Input('diarioDropdownRep', 'value'), Input('daterange', 'start_date'), Input('daterange', 'end_date')]
              )
def update_figure(diario, fechai, fechaf):
    fechai = dt.strptime(re.split('T| ', fechai)[0], '%Y-%m-%d')
    fechai_string = fechai.strftime('%d/%m/%Y')
    fechaf = dt.strptime(re.split('T| ', fechaf)[0], '%Y-%m-%d')
    fechaf_string = fechaf.strftime('%d/%m/%Y')
    df = dfrepeticioncategorias(dforig, fechai_string, fechaf_string)
    dfdiario = df[df['Diario'] == diario]
    fig = px.bar(dfdiario, y='Categoria', x='Count', color='Count', orientation='h')
    fig.layout = layout
    return fig


@app.callback([Output('barchart', 'figure'), Output('ngramscatter', 'figure')],
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
    dffreq1 = generardffrec(words)
    hist = px.bar(dffreq1.nlargest(rango, columns=['Frecuencia']), x='Palabra', y='Frecuencia', color='Frecuencia')
    hist.layout = layout
    bgs = generardffrecbgs(words)
    dffreq2 = preparardfbigramas(bgs)
    scat = px.scatter(dffreq2.nlargest(rango, columns=['Frecuencia']), x='Palabra', y='Frecuencia', size='Longitud',
                      color='Frecuencia', size_max=60)
    scat.layout = layout
    return hist, scat


@app.callback(Output('topicscatter', 'figure'),
              [Input('TopicRadioButtons', 'value'), Input('TopicDropdown', 'value')]
              )
def update_figure(diario, topic):
    if diario == 'Todos':
        df = dforig
    else:
        if diario == 'Clarin':
            df = dftopicclarin
        else:
            if diario == 'Infobae':
                df = dftopicinfobae
            else:
                df = dftopiclanacion

    df = df[df['Nombre_Topico'] == topic]
    scat = px.scatter(df, x='Titulo', y='Porcentaje_Contribucion', size='Porcentaje_Contribucion',
                      color='Porcentaje_Contribucion', size_max=10)
    scat.layout = layout
    return scat


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


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
