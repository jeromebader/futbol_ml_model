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

show_data = Blueprint('show_data', __name__)



@show_data.route('/show_data')
def showData():
    """ Function for fetching all data from DB and sending to render"""

    con, cursor = dbconn ()
    query = '''SELECT reactions, overall_rating, date, defensive_work_rate,attacking_work_rate, preferred_foot
        FROM Player_Attributes ORDER BY id ASC limit 0,100;
        '''
    df = sql_query(query,cursor)
    # pandas dataframe to html table flask
    uploaded_df_html = df.to_html(col_space='120px',justify='left')
    return render_template('show_csv_data.html', data_var = uploaded_df_html, num_data=50)