from flask import Flask
    
def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = "zaqwsxcderfvbgtyhnmjuik129838484734893"

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
