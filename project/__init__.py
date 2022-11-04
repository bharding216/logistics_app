from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import yaml
from flask_mysqldb import MySQL
import pymysql, cryptography



# General MySQL config format:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@server/db'


# Initialize the db
# db = SQLAlchemy(app)
db = SQLAlchemy()
#DB_NAME = 'carbon.db'


def create_app():
    app = Flask(__name__)

    db = yaml.full_load(open('db.yaml'))
    app.config['MYSQL_HOST'] = db['mysql_host']
    app.config['MYSQL_USER'] = db['mysql_user']
    app.config['MYSQL_PASSWORD'] = db['mysql_password']
    app.config['MYSQL_DB'] = db['mysql_db']

    app.config['SECRET_KEY'] = db['secret_key']


    #app.config['SECRET_KEY'] = "secret key"
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # New MySQL db connection:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:' + db['mysql_password'] + '@localhost/appointments'

    db.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix="/")

    from .auth import auth
    app.register_blueprint(auth, url_prefix="/")

    from .models import users
    #create_database(app)

    login_manager = LoginManager()
    # If the user is not logged in, redirect 
    # them to 'login.html'.
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return users.query.get(int(id))

    return app

#def create_database(app):
#    if not path.exists("project/" + DB_NAME):
#        db.create_all(app=app)