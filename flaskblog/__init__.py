from flask import Flask  # importing Flask class.

# Extension
from flask_sqlalchemy import SQLAlchemy  # Database
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Secret Key: Protect against modifying cookies and other attacks.
app.config['SECRET_KEY'] = '3c36493447a6e32d68167947ddac18ec'

# Set Up SQL Lite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Tell the extension where is the login route (for page_permission).
login_manager.login_message_category = 'info'  # Make the Flash Message Prettier with Bootstrap Class


from flaskblog import routes  # We need to do it after the creation of the app.
