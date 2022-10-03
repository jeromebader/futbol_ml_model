from flask import Flask, request, jsonify
from flask import Blueprint
import pymysql
import numpy as np
import pandas as pd
import os
from fileinput import filename
import numpy as np
import pandas as pd
import os
import sqlite3
from datetime import datetime


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def dbconn1 ():
    username = 'admin'
    password = '123456789'
    host = 'database.ctcaznptufxn.us-east-1.rds.amazonaws.com'
    port = 3306

    connection = pymysql.connect(host = host,
                     user = username,
                     password = password,
                     cursorclass = pymysql.cursors.DictCursor
    )

    cursor = connection.cursor()
    return connection, cursor


def dbconn ():
    connection = sqlite3.connect('./data/database.sqlite')
    cursor = connection.cursor()
    return connection, cursor


def sql_query(query,cursor):

    # Ejecuta la query
    cursor.execute(query)

    # Almacena los datos de la query 
    ans = cursor.fetchall()

    # Obtenemos los nombres de las columnas de la tabla
    names = [description[0] for description in cursor.description]

    return pd.DataFrame(ans,columns=names)


def replace_nan_mode(data):
    '''
    Funcion que rellena e iguala los valores de las columnas con la moda,
    para la correcta visualización y estudio del dataset.

    Args:
        data = dataset que contiene los datos con objeto de estudio.

    Returns: 
        dataframe listo para su estudio y visualización.
    '''
    iguala = [column for column in data.columns if data[column].isna().sum() > 0]

    for column in iguala:
        data[column] = data[column].fillna(data[column].value_counts().index[0])



def data_featuring (dfplayer):
    """Recibe dataframe y realiza feature engineering"""
    ## Feature Engineering
    # ignoramos valores nan del target porque representa muy poca cantidad
    dfplayer = dfplayer[dfplayer['overall_rating'].notna()]

    # Borramos columnas sin mucho aporte
    dfplayer = dfplayer.drop(columns=["defensive_work_rate","attacking_work_rate"])

    # Convertimos fecha en String to Datetime
    dfplayer['time'] = pd.to_datetime(dfplayer['date'].str.strip(), format='%Y-%m-%d')

    label_encoder = preprocessing.LabelEncoder()
    dfplayer['foot_preferred']= label_encoder.fit_transform(dfplayer['preferred_foot'])

    dfplayer = dfplayer.drop(columns=["preferred_foot", 'date'])

    replace_nan_mode(dfplayer)

    return dfplayer