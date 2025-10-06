from flask import Flask, current_app
from .settings import config
# from webapp.core.error_handlers import register_error_handlers
from .extensions import db, migrate
# from container import Container

def create_app() -> Flask:
    app = Flask(__name__)


    # # Inicjalizacja kontenera DI
    # #container = Container()
    # # To wdraza ustawienia z wiring_config w Container
    # #container.wire()
    #
    # # Mozesz w razie czego potem w dowolnym miejscu do tego kontenera sie odwolac (np. w testach)
    # # app.container = container
    #
    app.config.from_object(config['default'])
    config['default'].init_app(app)
    #
    # # register_error_handlers(app)
    # #app.register_blueprint(api_bp)
    #
    db.init_app(app)
    migrate.init_app(app, db)
    #
    # with app.app_context():
    #     import database.models
    #
    #     app.logger.info(f"SECRET KEY: {current_app.config['SECRET_KEY']}")
    #     app.logger.info(f'WEB APP NAME: {current_app.name}')
    #     app.logger.info(f'WEB APP ENDPOINTS: {current_app.url_map}')
    #     app.logger.info(f'WEB APP EXTENSTIONS: {current_app.extensions}')

    return app