import numpy as np
import pandas as pd
import os
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from datetime import datetime
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, explained_variance_score
from sklearn.ensemble import ExtraTreesRegressor
import pickle
from flask import Flask, request
from flask import Blueprint

app_model= Blueprint('app_model', __name__)

# print(os.getcwd())
# print (os.listdir())
os.chdir(os.path.dirname(os.path.abspath(__file__)))


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




@app_model.route("/app_model")
def app_models():


# Vemos las tablas en la DB
    conn, cursor = dbconn()
    res = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
    print ("tables:")
    for name in res:
        print(name[0])

    query = '''
    SELECT * 
    FROM Player_Attributes
    '''
    print ("--"*30)
    # Creamos dataframe
    dfplayer = sql_query(query,cursor)
    dfplayer.info()

    dfplayer = data_featuring(dfplayer)

    print ("--"*30)
    print ("training and prediction started, please wait!")
    ## Creamos el modelos
    #
    X = dfplayer.drop(columns=["overall_rating","time"])
    y = dfplayer[["overall_rating"]]

    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=40)

    model = ExtraTreesRegressor(n_estimators=130, random_state=0).fit(X_train, y_train)
    model.score(X_test, y_test)
    y_pred = model.predict(X_test)


    print("--"*30)
    print ("model results:")
    mse = mean_squared_error(y_test, y_pred)
    print("\tMean Squad Error:", mse )
    mae = mean_absolute_error(y_test, y_pred)
    print("\tMean absolute error:", mae)
    r2 = r2_score(y_test, y_pred)
    print("\tR2 score:",r2 )
    print("--"*30)



    # Guardamos el modelo
    tiempo = datetime.today().strftime('%Y%m%d%H%M%S')
    tiempo2 = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    filename = f'./model/finalized_model_{tiempo}.pkl'
    pickle.dump(model, open(filename, 'wb'))
    print (f"model saved as: {filename}")

    query = '''
       CREATE TABLE IF NOT EXISTS model_performance (id INTEGER, model_name Varchar (255) NOT NULL, 
       mae FLOAT NOT NULL,
       mse FLOAT NULL,
       r2 FLOAT NULL, 
       timestamp DATETIME NULL,  
       PRIMARY KEY("id" AUTOINCREMENT));  
       
        '''

    cursor.execute(query)
    inject = (filename,mae,mse,r2,tiempo2)

    query = '''
    INSERT INTO model_performance (model_name, mae, mse,r2,timestamp) VALUES (?, ?,?,?,?)
    
    '''

    cursor.execute(query,inject)
    conn.commit()
    conn.close()

    print ("--"*30)
    print ("End")

    return "Regression model created with success"

