from flask import Flask
from flask_login import LoginManager
from models import db, User
from datetime import timedelta
import os
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_caching import Cache
import click
from sqlalchemy import text

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # Redis Cache configuration
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')

    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_SECURE'] = not app.debug
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:password@db:5432/dashinfra')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    cache = Cache(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables
    with app.app_context():
        try:
            # Test the database connection
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        except Exception as e:
            print(f"Database connection error: {e}")
            
        db.create_all()

    # Register CLI commands
    @app.cli.command('create-admin')
    @click.argument('email')
    def create_admin(email):
        with app.app_context():
            if not User.query.filter_by(email=email).first():
                admin = User(username='admin', email=email, is_admin=True)
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                print('Admin user created')
            else:
                print('Admin user already exists')

    # Register routes
    from routes import register_routes
    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
