from flask import Flask  # importing Flask class.
from flask_sqlalchemy import SQLAlchemy  # Database

app = Flask(__name__)

# Secret Key: Protect against modifying cookies and other attacks.
app.config['SECRET_KEY'] = '3c36493447a6e32d68167947ddac18ec'

# Set Up SQL Lite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

from flaskblog import routes  # We need to do it after the creation of the app.
