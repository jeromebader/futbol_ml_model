import os
import sys
from flask import Flask, jsonify, request, render_template, session, redirect
import requests
module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *

## Link to the main APP
ingest_data= Blueprint('ingest_data', __name__)
#from src.api_monitor_model import monitor_model


# print(os.getcwd())
# print (os.listdir())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

### Arguments per JSON
@ingest_data.route("/ingest_data", methods=['POST'])
def ingest():
    """ Function for receiving new DATA by POST of arguments or JSON to the database"""
    message = ''
    data= {}
    if not request.is_json: 
        # Data by Argument received
       return "Data must be a Json"


    else:  # JSON data received
        request_data = request.get_json()
        df = pd.json_normalize(request_data )

        if 'date' in df.columns:
            print("ok")
        else:
            df["date"] = np.nan


        insanitas = []

        if request_data:

            query = '''
            SELECT * 
            FROM Player_Attributes
            '''
            
            conn,cursor = dbconn()
            cursor.execute(query)
            num_fields = len(cursor.description)
            field_names = [i[0] for i in cursor.description]
            print (field_names)
            print ("---")

            if df["date"].isna().sum():
                print ("date isna")
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
                df.date = df.date.fillna(timestampStr)
            
           
            df.fillna(0,inplace=True)

            for i in df.columns:
             if df[i].dtypes == "object":
          
            # ^(?=.*SELECT.*FROM)(?!.*(?:CREATE|DROP|UPDATE|INSERT|ALTER|DELETE|ATTACH|DETACH)).*$
            #SELECT\\s+?[^\\s]+?\\s+?FROM\\s+?[^\\s]+?\\s+?WHERE.*

                    # FILTER possible injections from JSON
                    try:
                            if df[i].str.contains('^SELECT|FROM|CREATE|DROP|UPDATE|INSERT|ALTER|DELETE|ATTACH|DETACH|WHERE', regex=True, na=False, case=False).any():
                                row = list(df[df.loc[:,i].str.contains('^SELECT|FROM|CREATE|DROP|UPDATE|INSERT|ALTER|DELETE|ATTACH|DETACH|WHERE', regex=True, na=False, case=False)].index) 
                                insanitas.append(row)
                                df.drop(row, axis=0, inplace=True)
                                print (f"Deleted because injection danger in colum {i}: ", row)

                    except:
                            pass
                   



            df = df.drop(columns=["id"])
            engine = creator_engine()
            df.to_sql('Player_Attributes', con=engine, if_exists='append',index=False)

            ## IF y value -> overall rating in JSON -> go to retrain
            if df["overall_rating"].all():
                print(df[df["overall_rating"] != 0].index)
                print ("Retrain")
                r = requests.get('http://localhost:5000/monitor_model','GET')
                print (type(r))
                print ("---")
                print (r.text)

            else:
                print ("prediction?")


            
         
    dfhtml = df.to_html()

    return dfhtml ### Message for data upload by API