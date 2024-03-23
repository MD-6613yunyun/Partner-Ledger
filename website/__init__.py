from flask import Flask
import psycopg2
    
def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = "zaqwsxcderfvbgtyhnmjuik129838484734893"
    app.secret_key = app.config['secret_key']

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin,url_prefix='/admin')

    return app

def db_connection():
    # Database connection details
    host = 'mdmmdblive.cedwkdu1rp7w.ap-southeast-1.rds.amazonaws.com'
    port = '5432'  # Default PostgreSQL port
    # port = '15769'
    database = 'mmm_uat'
    user = 'odoo'
    password = 'vOa6DHSd58W4'
    
    # Establish the database connection
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conn
    except psycopg2.Error as e:
        print('Error connecting to the database:', e)
