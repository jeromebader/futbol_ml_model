import os
from flask import Flask, request
from flask import Blueprint
import sys
module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *


app_model= Blueprint('app_model', __name__)

# print(os.getcwd())
# print (os.listdir())
os.chdir(os.path.dirname(os.path.abspath(__file__)))


@app_model.route("/app_model")
def app_models():


# Vemos las tablas en la DB
    conn, cursor = dbconn()
    # res = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'") ###
    # print ("tables:")
    # for name in res:
    #     print(name[0])

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

