import os
import sys
from flask import Flask, jsonify, request, render_template, session, redirect
import requests
module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *
from sklearn.model_selection import cross_val_score
from joblib import dump, load
os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

retrain_model = Blueprint('retrain_model', __name__)


@retrain_model.route("/retrain", methods=['GET'])
def retrain():

            # query = '''
            #         SELECT *
            #         FROM model_performancez
            # '''

            conn,cursor = dbconn()
            # cursor.execute(query)
            # print (cursor.fetchall())


            query2 = '''
            SELECT model_name, mae,mse,r2 FROM model_performancez WHERE id=(SELECT MAX(id) FROM model_performancez);
            '''

            # Reading previous model performance
            cursor.execute(query2)
            last_model = cursor.fetchall()
            print ("Last_model:",last_model)
            print(last_model[0][1])
            filename = last_model[0][0]
            mae_old = last_model[0][1]
            mse_old = last_model[0][2]
            r2_old = last_model[0][3]

            print ("retrieving data from DB")
            query = '''SELECT reactions, overall_rating, date, defensive_work_rate,attacking_work_rate, preferred_foot
        FROM Player_Attributes ORDER BY id ASC limit 0,300;
        '''
            print ("--"*30)
            # Creamos dataframe
            dfplayer = sql_query(query,cursor)
            dfplayer = data_featuring(dfplayer)

            print ("--"*30)
            print ("training and prediction started, please wait!")
            ## Creamos el modelos
            #
            # dfplayer.drop(columns=["overall_rating","time"])
            X = dfplayer[["reactions"]]
            y = dfplayer[["overall_rating"]]

            filename = filename.strip("'")
            model = load(filename)
            model.fit(X,y)
            y_pred = model.predict(X)

            #X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=40)
            y_test = y
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y%m%d%H")
            scores = cross_val_score(model, X, y, cv=10, scoring='neg_mean_absolute_error')
            filename = f'trained_model_{timestampStr}.joblib'
            dump(model, f'trained_model_{timestampStr}.joblib')

            print("--"*30)
            print ("model results:")
            mse = mean_squared_error(y_test, y_pred)
            print("\tMean Squad Error:", mse )
            mae = mean_absolute_error(y_test, y_pred)
            print("\tMean absolute error:", mae)
            r2 = r2_score(y_test, y_pred)
            print("\tR2 score:",r2 )
            print("--"*30)


            cursor.execute('''INSERT INTO model_performancez (model_name, mae, mse, r2) VALUES (%s, %s, %s, %s);''', (filename,round(float(mae),4),round(float(mse),4),round(float(r2),3), ))

            #cursor.execute(query2,inject)
            conn.commit()
            conn.close()

            message = f'<p style="color:green;"> Modelo entrenado y guardado {filename}  , MAE :' + str(abs(round(scores.mean(),2))) + '<p>'

            return render_template('index.html',msg_train=message)









