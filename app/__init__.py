from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from firebase_admin import credentials
import firebase_admin

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please login to access this page'
moment = Moment()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)

    cred = credentials.Certificate(app.config['GOOGLE_APPLICATION_CREDENTIALS'])
    firebase_admin.initialize_app(cred, {
        'storageBucket': app.config['FIREBASE_STORAGE_BUCKET']
    })

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


from app import models
