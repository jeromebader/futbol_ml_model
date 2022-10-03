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
import pymysql.cursors
import pymysql


def dbconn ():
    connection = pymysql.connect(host='database.ctcaznptufxn.us-east-1.rds.amazonaws.com',
                             user='admin',
                             password='123456789',
                             database='football_database'
                            )
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


conn, cursor = dbconn()
# res = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'") ###
# print ("tables:")
# for name in res:
#     print(name[0])

print(conn,cursor)

query = '''
SELECT * 
FROM Player_Attributes
'''
print ("--"*30)
# Creamos dataframe
dfplayer = sql_query(query,cursor)
dfplayer.info()