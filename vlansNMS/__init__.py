import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# load the environment variables
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
CORS(app)

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB')

from flask_sqlalchemy import SQLAlchemy

db_uri = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import vlansNMS.views.ui_views

import vlansNMS.models

db.create_all()
db.session.commit()
db.init_app(app)
migrate = Migrate(app, db)
