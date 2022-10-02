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
from datetime import datetime
import json
import re


def dbconn ():
    connection = sqlite3.connect('./data/database.sqlite')
    cursor = connection.cursor()
    return connection, cursor

## Link to the main APP
ingest_data= Blueprint('ingest_data', __name__)

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

            df.to_sql('Player_Attributes', con=conn, if_exists='append',index=False)

            ## IF y value -> overall rating in JSON -> go to retrain
            if df["overall_rating"].all():
                print(df[df["overall_rating"] != 0].index)
                print ("Retrain")

            else:
                print ("prediction?")
            
         
    dfhtml = df.to_html()

    return dfhtml ### Message for data upload by API