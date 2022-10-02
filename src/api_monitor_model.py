from fileinput import filename
import numpy as np
import pandas as pd
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, Blueprint
import pickle 

from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from datetime import datetime
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, explained_variance_score
from sklearn.ensemble import ExtraTreesRegressor

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

## Link to the main APP
monitor_model = Blueprint('monitor_model', __name__)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

### Arguments per JSON
@monitor_model.route("/monitor_model", methods=['GET'])
def monitor():

            query = '''
                    SELECT * 
                    FROM model_performance
            '''
            
            conn,cursor = dbconn()
            result = cursor.execute(query)
            print (result.fetchall())


            query = '''
            SELECT model_name, mae,mse,r2 FROM model_performance WHERE id=(
            SELECT max(id) FROM model_performance
                                        )

            
            '''

            # Reading previous model performance
            result = cursor.execute(query)
            last_model = result.fetchall()
            print ("Last_model:",last_model)
            filename = last_model[0][0]
            mae_old = last_model[0][1]
            mse_old = last_model[0][2]
            r2_old = last_model[0][2]


            query = '''
            SELECT * 
            FROM Player_Attributes
            '''
            print ("--"*30)
            # Creamos dataframe
            dfplayer = sql_query(query,cursor)
            dfplayer = data_featuring(dfplayer)

            print ("--"*30)
            print ("training and prediction started, please wait!")
            ## Creamos el modelos
            #
            X = dfplayer.drop(columns=["overall_rating","time"])
            y = dfplayer[["overall_rating"]]

            X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=40)
            model = pickle.load(open(filename,'rb'))
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

            if mae<mae_old and mse<mse_old and r2<r2_old:
                message = "Performance of model lower than before, sending to training"
                ### CALLING API OF TRAINING
            
            else:
                message = "Performance of model is higher than before, training not necessary"


            return message