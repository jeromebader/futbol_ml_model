
import os
import sqlite3
import pymysql
import sys

module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from general_functions import *

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