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
from flask import Flask, request, jsonify
from flask import Blueprint
import pymysql

db_connect= Blueprint('db_connect', __name__)

# print(os.getcwd())
# print (os.listdir())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

@db_connect.route('/db_connect', methods=['GET'])
def dbconnect():

    username = 'admin'
    password = '123456789'
    host = 'database.ctcaznptufxn.us-east-1.rds.amazonaws.com'
    port = 3306

    db = pymysql.connect(host = host,
                     user = username,
                     password = password,
                     cursorclass = pymysql.cursors.DictCursor
    )

    cursor = db.cursor()

    cursor.connection.commit()
    use_db = ''' USE football_database'''
    cursor.execute(use_db)

    sql = '''SELECT overall_rating FROM Player_Attributes limit 0,10;

    '''
    cursor.execute(sql)
    mi_tabla = cursor.fetchall()
    db.close()
    return jsonify(mi_tabla)