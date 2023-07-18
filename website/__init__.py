from flask import Flask
import psycopg2
    
def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = "zaqwsxcderfvbgtyhnmjuik129838484734893"

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin,url_prefix='/admin')

    return app

def db_connection():
    # Database connection details
    host = '192.168.0.60'
    # host = '0.tcp.ap.ngrok.io'
    # host = '172.30.32.183'
    port = '5432'  # Default PostgreSQL port
    # port = '15769'
    database = 'mmm_uat'
    user = 'postgres'
    password = 'admin'
    
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
