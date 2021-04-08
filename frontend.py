# -*- coding: utf-8 -*-
from datetime import datetime as dt
from datetime import timedelta
from datetime import date as Date
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import re
import os
import sqlite3
import plotly.graph_objects as go
#import plotly.express as px
import backend as feedDB
import base64

## CONSTANTES
database = os.path.dirname(os.path.realpath(__file__))+'/DataBase.db'
MaxRange = 10000 #Echelle max en ordonnée (kW)


def DateRangeForFig2_BASE_start_date(database):
    sqliteConnection = feedDB.connectToDatabase(database)
    records = feedDB.readTable(sqliteConnection, "BASE_daily_mean_power")
    feedDB.closeDataBase(sqliteConnection)
    records.sort()
    return feedDB.convertFromTimestampToDatetime(records[0][0])

def serve_layout():
    layout = html.Div([
        # first line
        html.Div([
            # first column
            html.A([
                dcc.Graph(
                    id='gauge',
                    # figure=figGauge,
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=10*1000, # in milliseconds
                    n_intervals=0
                    ),
            ], className='three columns', style={'margin-top': '0px', 'margin-bottom': '0px', 'textAlign': 'bottom', 'border': '3px solid white', "text-decoration":"none"}, target="_blank"),   # , 'width':'17.3%'
            # middle column
            html.A([
                #html.Div(id='output-container-date-picker-single'),
                html.H1(children='WILLEE', style={'margin-top': '0px', 'margin-left': '0px','margin-bottom': '0px', 'margin-right': '0px', 'color': 'black', 'fontsize':'5'}),
                # html.A([
                #     html.H1(children='', style={'margin-top': '0px', 'margin-left': '0px', 'color':'black'} ),
                #     ], className='four columns', style={'textAlign': 'left', 'border': '3px solid white', "text-decoration":"none", 'margin-top': '0px', 'margin-left': '0px'}, href='/', target="_blank"),
                html.A([
                    html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
                        open(os.path.dirname(os.path.realpath(__file__)) + '/logos/logoGitHub.png', 'rb').read()).decode('ascii')), alt=':(', style={'height': '50px', 'margin-top': '0px', 'margin-left': '0px', 'position': 'relative', 'border': '1px solid white'}),
                    ], style={'textAlign': 'center', 'border': '3px solid white', "text-decoration":"none", 'margin-top': '0px', 'margin-left': '35px'}, href='https://github.com/willeeLinky/WILLEE', target="_blank"),
                # html.A([
                #     html.H1(children='', style={'margin-top': '0px', 'margin-left': '0px', 'color':'black'} ),
                #     ], className='four columns', style={'textAlign': 'center', 'border': '3px solid white', "text-decoration":"none", 'margin-top': '0px', 'margin-left': '0px'}, href='', target="_blank")
            ], className='six columns', style={'textAlign': 'center', 'border': '3px solid white', "text-decoration":"none"}, href='', target="_blank"),
            # last column
            html.A([
                html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open(os.path.dirname(os.path.realpath(__file__))+'/logos/LogoFinalWILLEE.png', 'rb').read()).decode('ascii')), alt = ':(', style = {'height': '160px', 'width': '240px', 'margin-top': '0px', 'margin-left': '-50px',
                                     'position': 'relative', 'border': '1px solid white'}),
            ], className='three columns', style={'textAlign': 'right', 'margin-left': '1%', 'border': '3px solid white'}, href='', target="_blank"),
        ], className='row', style={'border': '1px solid white'}),
        html.Hr(),
        # second line
        html.H4(id='TitreAvantFig1'),
        html.Div([
            html.Div([
                html.P(children='Date (choisir) : ', style={'margin-top': '+10px', 'margin-left': '10px'}),
                dcc.DatePickerSingle(
                    id='ChoixDateFig1',
                    min_date_allowed=DateRangeForFig2_BASE_start_date(database),
                    max_date_allowed=Date.today(),
                    # initial_visible_month=Date.today() - timedelta(days=58),
                    # start_date=DateRangeForFig2_BASE_start_date(database),
                    #initial_visible_month=dt.today(),
                    #date = str(dt.today()),
                    #date= str(Date.today()) +  " 23:59:59"  ,
                    date= str(Date.today()),
                    first_day_of_week = 1, # first column is monday when set to 1
                    display_format='DD MMM YY',
                    style={'margin-left': '10px'}
                ),
                html.P(children='Echelle : ', style={'margin-top': '+10px', 'margin-left': '10px'}),
                dcc.RadioItems(
                    id='LinOrLogButtonForFig1',
                    options=[{'label': i, 'value': i} for i in ['Linéaire', 'Log']],
                    value='Linéaire',
                    #labelStyle={'display': 'inline-block'},
                    style = {'margin-top': '+10px', 'margin-left': '10px'}
                ),
                html.P(children='Chargement : ', style={'margin-top': '+10px', 'margin-left': '10px'}),
                dcc.RadioItems(
                    id='HighLowSamplingButtonForFig1',
                    options=[{'label': i, 'value': i} for i in ["Rapide et imprécis \n (1min/point)", "Lent et précis \n (2sec/point)"]],
                    value="Rapide et imprécis \n (1min/point)",
                    #labelStyle={'display': 'inline-block'},
                    style = {'margin-top': '+10px', 'margin-left': '10px'}
                )
            ], className='two columns', style={'border': '3px solid white', 'margin-left': '0%', 'margin-right': '0%', 'width':'17.3%'}),
            html.Div([
                dcc.Graph(
                    id='powerVsTime_figure',
                    #figure=fig,
                    style = {'margin-top': '0px'},
                ),
                dcc.Interval(
                    id='intervalGraphPowerVsTime',
                    interval=1*60*1000, # in milliseconds
                    n_intervals=0
                    ),
            ], className='ten columns', style={'border': '3px solid white', 'margin-left': '0%', 'margin-right': '0%'})
        ], className='row', style={'border': '3px solid white', 'margin-left': '0%', 'margin-right': '0%'}),
        html.Hr(), # a simple grey line
        # third line
        html.Div([
            html.H4(id='TitreAvantFig2_BASE'),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='daily_mean_power_figure_BASE',
                        #figure=fig_mean_power
                    )], className='nine columns', style={'border': '3px solid white'}
                ),
                html.Div([
                    html.H6(children='Période :'),
                    html.Div([
                        dcc.DatePickerRange( #https://dash.plotly.com/dash-core-components/datepickerrange
                            id='DateRangeForFig2_BASE',
                            min_date_allowed=DateRangeForFig2_BASE_start_date(database),
                            max_date_allowed=Date.today(),
                            initial_visible_month=Date.today()-timedelta(days=28),
                            start_date=DateRangeForFig2_BASE_start_date(database),
                            end_date=Date.today()-timedelta(days=0),
                            display_format='DD MMM YY',
                            number_of_months_shown=2
                        )]),
                        html.H6(children='Prix du kWh (€/kWh) :'),
                        dcc.Input(id='InputPrixkWh_BASE', value=0.1960, type='text'),  # essayer type float ???
                        #html.H6(children='Coût estimé (€) :'),
                        html.H6(id='CoutEstime_BASE'),
                        #html.H6(children='Conso estimée (kWh) :'),
                        html.H6(id='ConsoEstimee_BASE'),
                        html.H6(children='Affichage :'),
                        dcc.RadioItems(
                            id='EuroOrkWhButtonForFig2_BASE',
                            options=[{'label': i, 'value': i} for i in ['kWh', '€']],
                            value='kWh',
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.H6(children='Lissage (jours) :'),
                        dcc.Slider(
                            id='choixLissage',
                            min=1,
                            max=31,
                            step=2,
                            marks={1:"1j",3:"3j",7:"7j",11:"11j",15:"15j",19:"19j",23:"23j",27:"27j",31:"31j"},
                            #marks={2*i-1 : str(2*i-1)+'j' for i in range(17)},
                            value=3
                        )
                    ], className='three columns', style={'border': '3px solid white', 'margin-left': '0%', 'margin-right': '0%', 'width':'26%'}
                ),
            ], className='row', style={'border': '3px solid white'}),
        ]),
        html.Hr(),
    ])
    return layout

app = dash.Dash(__name__ )
app.layout = serve_layout
app.title = 'WILLEE'


@app.callback(
    dash.dependencies.Output('gauge', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_output(n):
    tableCurrentData = "CurrentData"
    sqliteConnection = feedDB.connectToDatabase(database)
    recordsCurrentDB = feedDB.readTable(sqliteConnection, tableCurrentData)
    feedDB.closeDataBase(sqliteConnection)
    PAPP_tuple = [item for item in recordsCurrentDB if item[0] == 'PAPP']
    PAPPValue = int(PAPP_tuple[0][1])
    figGauge = go.Figure(go.Indicator( #https://plotly.com/python/gauge-charts/
        mode="gauge+number",
        # value=int(time.time())%60,
        value = PAPPValue,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge = {'axis': {'range': [None, MaxRange], 'tickwidth': 1, 'tickcolor': "darkblue"},
                 'steps' : [
                     {'range': [0, 0.5*MaxRange], 'color': "lightgray"},
                     {'range': [0.5*MaxRange, 0.8*MaxRange], 'color': "darkgray"},
                     {'range': [0.8*MaxRange, 1*MaxRange], 'color': "gray"}],
                 # 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 300}
                 },
        number_valueformat=".2d",
        number_font_size = 15,
        title_font_size=15,
        title={'text': "Puissance apparente actuelle (VA) : "}
    ))
    figGauge.update_layout(
        autosize=False,
        width=300,
        height=200,
        margin=dict(
            l=50,
            r=50,
            b=0,
            t=20,
            pad=4
        ),
    )
    # figGauge.update_traces(number_font_size=15, selector = dict(type='indicator'))
    # figGauge.update_traces(number_valueformat= ".2d", selector = dict(type='indicator'))
    # fig.update_traces(title_font_size= 15, selector = dict(type='indicator'))
    return figGauge



@app.callback(
    Output('powerVsTime_figure', 'figure'),
    [Input('ChoixDateFig1', 'date'),
     Input('LinOrLogButtonForFig1', 'value'),
     Input('HighLowSamplingButtonForFig1', 'value'),
     Input('intervalGraphPowerVsTime', 'n_intervals'),])
def update_figure_powerVsTime(date,LinOrLogButtonForFig1,HighLowSamplingButtonForFig1, n):
    decimatioNfactor = 30  # 15 => 30s/pt   30 => 1min/pt
    sqliteConnection = feedDB.connectToDatabase(database)
    selectedDay = str("day_" + str(date).replace("-", "_"))
    records = feedDB.readTable(sqliteConnection, selectedDay)
    feedDB.closeDataBase(sqliteConnection)
    # records renvoie une liste de tuples (time, power) ; il faut deux listes
    abscisse = [dt.fromtimestamp(int(tuple[0])) for tuple in records]
    ordonnee = [int(tuple[1]) for tuple in records]
    if HighLowSamplingButtonForFig1 == "Rapide et imprécis \n (1min/point)":
        abscisse.reverse()
        ordonnee.reverse()
        abscisse = abscisse[::decimatioNfactor]
        ordonnee = ordonnee[::decimatioNfactor]
    fig = go.Figure(data=[go.Scatter(x= abscisse , y=ordonnee)])
    if LinOrLogButtonForFig1=='Log':
        fig.update_layout(yaxis_type="log", yaxis_range=[1, 4])
    else:
        fig.update_layout(yaxis_range=[0, 1*MaxRange])
    fig.update_layout(
        #title=str("Consommation du "+ str(dt.strftime(dt.strptime(date, '%Y-%m-%d'), '%d/%m/%Y'))+" :"),
        xaxis_title="Temps (Heure:Min:Sec)",
        yaxis_title="Puissance instantannée consommée(W)",
        #margin=dict(autoexpand=False, l=0, r=0, t=0,),
        #grid=dict(color='red')
        #plot_bgcolor='red',
        #font=dict(family="Courier New, monospace", size=18, color="#7f7f7f")
    )
    return fig

@app.callback(
    Output('daily_mean_power_figure_BASE', 'figure'),
    [Input('DateRangeForFig2_BASE', 'start_date'),
     Input('DateRangeForFig2_BASE', 'end_date'),
     Input('EuroOrkWhButtonForFig2_BASE', 'value'),
     Input('InputPrixkWh_BASE', 'value'),
     Input('choixLissage', 'value'),
     Input('ChoixDateFig1', 'date')])
def update_mean_power_figure_BASE(start_date, end_date, EuroOrkWh, InputPrixkWh, Lissage, dateCalendrierFig1):
    tableName = "BASE_daily_mean_power"
    tableCurrentData = "CurrentData"
    sqliteConnection = feedDB.connectToDatabase(database)
    records = feedDB.readTable(sqliteConnection, tableName)
    recordsCurrentDB = feedDB.readTable(sqliteConnection, tableCurrentData)
    BASE_tuple = [item for item in recordsCurrentDB if item[0] == 'BASE']
    # records renvoie une liste de tuples (Datedepuis1970, puissanceBASEaMinuit) ; il faut deux listes
    abscisse = [feedDB.convertFromTimestampToDatetime(tuple[0]) for tuple in records]
    ord = [tuple[1] for tuple in records]
    ord.append(int(BASE_tuple[0][1])) # ajoute la valeur courante de "BASE"
    ordonnee = list()
    for ind in range(0, (len(ord) - 1)):
        ordonnee.append( (ord[ind + 1] - ord[ind])/1000 )
    start_date_datetimeFormat = dt(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10]))
    end_date_datetimeFormat = dt(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))
    min_range = 0
    max_range = 30
    def moyenne_glissante(valeurs, intervalle):
        indice_debut = (intervalle - 1) // 2
        liste_moyennes = [sum(valeurs[i - indice_debut:i + indice_debut + 1]) / intervalle for i in
                          range(indice_debut, len(valeurs) - indice_debut)]
        # Gestion des bords :
        for k in range((intervalle - 1) // 2):
            value = valeurs[0]
            value2 = valeurs[-1]
            for m in range(1, 2 * k + 1):
                value = valeurs[m] + value
            value = value / (2 * k + 1)
            liste_moyennes.insert(k, value)
            for m in range(len(valeurs) - (2 * k + 1), len(valeurs) - 1):
                value2 = valeurs[m] + value2
            value2 = value2 / (2 * k + 1)
            liste_moyennes.insert(len(liste_moyennes) - k, value2)
        return liste_moyennes

    if float(Lissage) > 1:
        courbeLissee = moyenne_glissante(ordonnee, Lissage)
        if EuroOrkWh == '€':
            coeff = float(InputPrixkWh)
            ordonnee = [float("%.2f" % float(number * coeff)) for number in ordonnee]
            trace2 = go.Scatter(x=abscisse, y=[el*coeff for el in courbeLissee], name='Lissage', marker_color="blue")
            colors = ["rgb(148,185,243)"] * len(ordonnee)
            colors[feedDB.IndexOfClosestDate(abscisse, dateCalendrierFig1)] = 'red'
            fig = go.Figure([ go.Bar(x=abscisse, y=ordonnee, marker_color=colors), trace2 ])
            fig.update_layout(
                xaxis_range=[start_date_datetimeFormat - timedelta(days=1),
                             end_date_datetimeFormat + timedelta(days=1)],
                yaxis_range=[min_range, max_range * coeff],
                xaxis_title="Jour",
                yaxis_title="Coût quotidien (€)",
                showlegend=False,
            )
        else:
            trace2 = go.Scatter(x=abscisse, y=courbeLissee, name='Lissage', marker_color="blue")
            colors = ["rgb(148,185,243)"] * len(ordonnee)
            colors[feedDB.IndexOfClosestDate(abscisse, dateCalendrierFig1)] = 'red'
            fig = go.Figure([ go.Bar(x=abscisse, y=ordonnee, marker_color=colors), trace2 ])
            fig.update_layout(
                xaxis_range=[start_date_datetimeFormat - timedelta(days=1),
                             end_date_datetimeFormat + timedelta(days=1)],
                yaxis_range=[min_range, max_range],
                xaxis_title="Jour",
                yaxis_title="Energie quotidienne consommée (kWh)",
                showlegend=False,
            )
    else:
        if EuroOrkWh=='€':
            coeff=float(InputPrixkWh)
            ordonnee = [float("%.2f" % float(number*coeff)) for number in ordonnee]
            colors = ['blue', ] * len(ordonnee)
            colors[feedDB.IndexOfClosestDate(abscisse, dateCalendrierFig1)] = 'red'
            fig = go.Figure([go.Bar(x=abscisse, y=ordonnee, marker_color=colors)])
            fig.update_layout(
                xaxis_range=[start_date_datetimeFormat - timedelta(days=1), end_date_datetimeFormat + timedelta(days=1)],
                yaxis_range=[min_range, max_range*coeff],
                xaxis_title="Jour",
                yaxis_title="Coût quotidien (€)",
            )
        else:
            colors = ['blue', ] * len(ordonnee)
            colors[feedDB.IndexOfClosestDate(abscisse, dateCalendrierFig1)] = 'red'
            fig = go.Figure([go.Bar(x=abscisse, y=ordonnee, marker_color=colors)])
            fig.update_layout(
                xaxis_range=[start_date_datetimeFormat - timedelta(days=1), end_date_datetimeFormat + timedelta(days=1)],
                yaxis_range=[min_range, max_range],
                xaxis_title="Jour",
                yaxis_title="Energie quotidienne consommée (kWh)",
            )
    feedDB.closeDataBase(sqliteConnection)
    return fig

@app.callback(
    Output('TitreAvantFig1', 'children'),
    [Input('ChoixDateFig1', 'date')])
def update_title_of_powerVsTimeFigure(date):
    return str("Consommation du " + str(dt.strftime(dt.strptime(date, '%Y-%m-%d'), '%d/%m/%Y')) + " :"),

@app.callback(
    Output('TitreAvantFig2_BASE', 'children'),
    [Input('DateRangeForFig2_BASE', 'start_date'),
     Input('DateRangeForFig2_BASE', 'end_date')])
def update_title_of_powerVsTimeFigure(start_date,end_date):
    start_date_datetimeFormat = dt(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10]))
    start_date_DDxMMxYYYYFormat = dt.strftime(start_date_datetimeFormat, '%d/%m/%Y')
    end_date_datetimeFormat = dt(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))
    end_date_DDxMMxYYYYFormat = dt.strftime(end_date_datetimeFormat, '%d/%m/%Y')
    msg = str("Consommation quotidienne sur la période du "
    + start_date_DDxMMxYYYYFormat + " au " + end_date_DDxMMxYYYYFormat + " :")
    return msg

@app.callback(
    Output('ConsoEstimee_BASE', 'children'),
    [Input('DateRangeForFig2_BASE', 'start_date'),
     Input('DateRangeForFig2_BASE', 'end_date')])
def EstimateConsokWh(start_date,end_date):
    """start_date has form : '2020-11-01T00:00:00' """
    start_date_timestamp = feedDB.convertFromGUIInDateToTimeStamp(start_date)
    end_date_timestamp = feedDB.convertFromGUIInDateToTimeStamp(end_date) + 86400 # Ajouter 1jour car si on veut la conso de jeudi à samedi compris, il faut chercher le point de dimanche matin
    tableName = "BASE_daily_mean_power"
    sqliteConnection = feedDB.connectToDatabase(database)
    records = feedDB.readTable(sqliteConnection, tableName)
    instant = [element[0] for element in records]
    power = [element[1] for element in records]
    # myList.index(min(myList, key=lambda x: abs(x - myNumber)))
    start_index = instant.index(min(instant, key=lambda x: abs(x - start_date_timestamp))) # returns index closest
    end_index = instant.index(min(instant, key=lambda x: abs(x - end_date_timestamp))) # returns index closest
    cumulativePower = (power[end_index]-power[start_index])/1000
    return str('Conso. estimée : '+str(float("%.2f" % float(cumulativePower))) + ' kWh')

@app.callback(
    Output('CoutEstime_BASE', 'children'),
    [Input('DateRangeForFig2_BASE', 'start_date'),
     Input('DateRangeForFig2_BASE', 'end_date'),
     Input('InputPrixkWh_BASE', 'value')])
def EstimateConsoEuro(start_date,end_date,value):
    value = float(value)
    start_date_timestamp = feedDB.convertFromGUIInDateToTimeStamp(start_date)
    end_date_timestamp = feedDB.convertFromGUIInDateToTimeStamp(end_date) + 86400 # Ajouter 1jour car si on veut la conso de jeudi à samedi compris, il faut chercher le point de dimanche matin
    tableName = "BASE_daily_mean_power"
    sqliteConnection = feedDB.connectToDatabase(database)
    records = feedDB.readTable(sqliteConnection, tableName)
    instant = [element[0] for element in records]
    power = [element[1] for element in records]
    # myList.index(min(myList, key=lambda x: abs(x - myNumber)))
    start_index = instant.index(min(instant, key=lambda x: abs(x - start_date_timestamp))) # returns index closest
    end_index = instant.index(min(instant, key=lambda x: abs(x - end_date_timestamp))) # returns index closest
    cumulativePower = (power[end_index]-power[start_index])/1000
    return str("Coût estimé : "+str(float("%.2f" % float(cumulativePower*value))) + ' €')

if __name__ == '__main__':
    # database = os.path.dirname(os.path.realpath(__file__))+'/SQLite_Python3_22112020.db'
    app.run_server(debug=False, host='0.0.0.0', port=8050)
