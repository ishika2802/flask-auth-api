from flask import Flask, redirect, url_for, request, current_app, session, render_template
import os
from os import path
from flask_pymongo import PyMongo
from pymongo import MongoClient 
from flask_session import Session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user,UserMixin
from bson import ObjectId
from flask_mail import Mail, Message

def create_app():
    # Specify the template folder dynamically
    # app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
    app = Flask(__name__, static_url_path='/static', static_folder=os.path.join(os.getcwd(), 'static/assets'), template_folder=os.path.join(os.getcwd(), 'templates'))

    # App secret key
    # App secret key
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem or another supported type
    Session(app)

    # Initialize MongoDB client
    mongo_uri = "MONGODBCONNECTIONLINK"
    client = MongoClient(mongo_uri)
    app.mongo_client = client
    app.db = client['DBNAME']

    # Initialize the login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.loginUser'
    login_manager.login_message = "Please log in to access this page."
    
    # User class should inherit from UserMixin to work with Flask-Login
    class User(UserMixin):
        def __init__(self, id, username, email):
            self.id = str(id)  # id must be a string, for Flask-Login compatibility
            self.username = username
            self.email = email

    @login_manager.user_loader
    def load_user(user_id):
        user_data = app.db['users'].find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data['_id'], user_data['userName'], user_data['email'])
        return None


    # Test MongoDB connection
    try:
        client.admin.command('ping')
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e
    
    # Configure the app with settings for Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587  # TLS port
    app.config['MAIL_USE_TLS'] = True  # Use TLS instead of SSL
    app.config['MAIL_USE_SSL'] = False  # Set SSL to False
    app.config['MAIL_USERNAME'] = "username@mail.com"
    app.config['MAIL_PASSWORD'] = "16 character"
    app.config['MAIL_DEFAULT_SENDER'] = "username@mail.com"
    
    mail = Mail(app)
    mail.init_app(app)

    
    # Import blueprints
    from app.views import views
    from app.auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    @app.before_request
    def handle_redirect_to_login():
        # Check if the user is not authenticated and trying to access a protected page
        if not current_user.is_authenticated:
            session.clear()  # Clear residual session data
            if request.endpoint not in ['auth.loginUser', 'auth.registerUser', 'auth.resetUserPassword', 'auth.reset_password', 'static']:
                return redirect(url_for('auth.loginUser', next=request.url))

    return app  # Returns the Flask application instance