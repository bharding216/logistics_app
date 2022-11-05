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
    #db = yaml.full_load(open('project/db.yaml'))
    #app.config['MYSQL_HOST'] = db['mysql_host']
    #app.config['MYSQL_USER'] = db['mysql_user']
    #app.config['MYSQL_PASSWORD'] = db['mysql_password']
    #app.config['MYSQL_DB'] = db['mysql_db']
    #app.config['SECRET_KEY'] = db['secret_key']
    app.config['SECRET_KEY'] = 'my key'

    # Initialize plugins
    db.init_app(app)
    login_manager.init_app(app)

    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:' + db['mysql_password'] + '@localhost/trucks'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Monkey216@localhost/trucks'

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