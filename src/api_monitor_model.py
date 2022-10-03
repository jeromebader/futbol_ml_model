
import os
import sys

module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *


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