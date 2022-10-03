import os
import sys
from flask import Flask, jsonify, request, render_template, session, redirect
import requests
module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *
from sklearn.model_selection import cross_val_score

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

retrain_model = Blueprint('retrain_model', __name__)


@retrain_model.route("/retrain", methods=['GET'])
def retrain():

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
            
            model = pickle.load(open(filename,'rb'))
            model.fit(X,y)

            X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=40)
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y%m%d%H%")
            scores = cross_val_score(model, X, y, cv=10, scoring='neg_mean_absolute_error')
            model = pickle.load(open(f'new_model_{timestampStr}','wb'))


            return "New model retrained and saved as advertising_model_v1. The results of MAE with cross validation of 10 folds is: " + str(abs(round(scores.mean(),2)))









