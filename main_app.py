import os
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from flask import Flask, jsonify, request, render_template, session, redirect
import numpy as np
import pandas as pd
import pickle 
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

import sys
 
# adding Folder_2 to the system path
sys.path.insert(0, '/src')
print (os.getcwd())
from src.api_create_model import app_model
from src.api_ingesta_data import ingest_data

app = Flask(__name__)

os.chdir(os.path.dirname(__file__))

#*** Flask configuration
 
# Define folder to save uploaded files to process further
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploads/')
 
# Define allowed files for uploading (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv'}
 
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["DEBUG"] = True

# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
# Define secret key to enable session
app.secret_key = 'futbolMadrid2022'


## Register blueprints
app.register_blueprint(app_model)
app.register_blueprint(ingest_data)



@app.route("/")
def main():
    """Function for rendering the main page"""
    
    return render_template('index.html')

#if __name__ == "__main__":
app.run()