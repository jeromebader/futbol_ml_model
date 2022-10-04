
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from flask import Flask, request, jsonify
from flask import Blueprint
import requests
import sys
module_path = os.path.dirname(os.path.abspath(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)
from src.general_functions import *


# adding Folder_2 to the system path

print (os.getcwd())

app = Flask(__name__)


os.chdir(os.path.dirname(__file__))

#*** Flask configuration

# Define folder to save uploaded files to process further
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'uploads/')

# Define allowed files for uploading (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'json'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["DEBUG"] = True

# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define secret key to enable session
app.secret_key = 'futbolMadrid2022'

## Register blueprints
from src.api_create_model import app_model
from src.api_ingesta_data import ingest_data
from src.api_monitor_model import monitor_model
from src.api_connect_test import db_connect
from src.api_new_model import retrain_model
from src.api_predict import predict
from src.api_show_data import show_data
from src.api_upload_json import uploads

app.register_blueprint(app_model)
app.register_blueprint(ingest_data)
app.register_blueprint(monitor_model)
app.register_blueprint(db_connect)
app.register_blueprint(retrain_model)
app.register_blueprint(predict)
app.register_blueprint(show_data)
app.register_blueprint(uploads)


@app.route("/")
def main():
    """Function for rendering the main page"""

    return render_template('index.html')

#if __name__ == "__main__":
#app.run()