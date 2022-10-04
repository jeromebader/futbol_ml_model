import os
import sys
from flask import Flask, jsonify, request, render_template, session, redirect
import requests
module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *



os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

predict = Blueprint('predict', __name__)


@predict.route("/predict", methods=['GET'])
def predictions():


    conn,cursor = dbconn()

    query2 = '''
            SELECT model_name, mae,mse,r2 FROM model_performancez WHERE id=(SELECT MAX(id) FROM model_performancez);
            '''

    # Reading previous model performance
    cursor.execute(query2)
    last_model = cursor.fetchall()
    print ("Last_model:",last_model)
    print(last_model[0][1])
    filename = last_model[0][0]


    print ("retrieving data from DB")
    try:
        query = '''SELECT reactions, overall_rating, date, defensive_work_rate,attacking_work_rate, preferred_foot
        FROM Player_Attributes ORDER BY id ASC limit 0,500;
        '''
        dfplayer = sql_query(query,cursor)
    except:
         query = '''
                SELECT reactions, overall_rating, date, defensive_work_rate,attacking_work_rate, preferred_foot
                FROM Player_Attributes ORDER BY id ASC limit 0,500;
                '''
         dfplayer = sql_query(query,cursor)

    #dfplayer = dfplayer[dfplayer["overall_rating"].isna()]



    print ("--"*30)
    print (dfplayer)
    # Creamos dataframe
    #dfplayer = sql_query(query,cursor)
    #dfplayer = dfplayer[~dfplayer["reactions"].isna()]

    dfplayer = data_featuring(dfplayer)

    print (dfplayer)
    print ("--"*30)
    print ("training and prediction started, please wait!")
    ## Creamos el modelos
    #
    # dfplayer.drop(columns=["overall_rating","time"])
    X = dfplayer[["reactions"]]
    #y = dfplayer[["overall_rating"]]

    #X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=40)

    #with open(filename, 'wb') as f:
       # pickle.dump(model, f,protocol=2)
    filename = filename.strip("'")
    #print (filename)
    #f = open(filename, "r")
    #print(f.read())
    print ("--"*20)

    #sys.path.append(module_path)
    #with open(filename, 'rb') as fs:
          #  model = pickle.load(fs)

    model = load(filename)
    #model = pickle.load(open(filename,'rb'))
    results = model.predict(X)
    df_new = dfplayer
    df_new["Est_overall_rating"] = np.round(results,2)
    if request.method == "POST":
        html_df = df_new.to_json()
        return   html_df
    else:
        html_df = df_new.to_html(col_space='160px',justify='left')
        return render_template('show_predictions.html', data_var = html_df)