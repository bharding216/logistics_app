from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import yaml
from flask_mysqldb import MySQL
import pymysql, cryptography


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Application configuration
    with open('project/db.yaml', 'r') as file:
        test = yaml.load(file, Loader=yaml.FullLoader)
    app.config['MYSQL_HOST'] = test['mysql_host']
    app.config['MYSQL_USER'] = test['mysql_user']
    app.config['MYSQL_PASSWORD'] = test['mysql_password']
    app.config['MYSQL_DB'] = test['mysql_db']
    app.config['SECRET_KEY'] = test['secret_key']
    #app.config['SECRET_KEY'] = 'my key'

    # Initialize plugins
    db.init_app(app)
    login_manager.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + test['mysql_user'] + \
        ':' + test['mysql_password'] + '@' + test['mysql_host'] + '/' + test['mysql_db']
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Monkey216@localhost/trucks'
    #[DB_TYPE]+[DB_CONNECTOR]://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]

    # General MySQL config format:
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@server/db'

    with app.app_context():
        from .views import views
        from .auth import auth       
        from .models import users

        app.register_blueprint(views, url_prefix="/")
        app.register_blueprint(auth, url_prefix="/")

        # Create database models
        db.create_all()

        # If the user is not logged in, redirect 
        # them to 'login.html'.
        login_manager.login_view = "auth.login"

        @login_manager.user_loader
        def load_user(id):
            return users.query.get(int(id))

        return app


#def create_database(app):
#    if not path.exists("project/" + DB_NAME):
#        db.create_all(app=app)