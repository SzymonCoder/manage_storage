from flask import Flask, current_app

from . import database
from .api import api_bp
from .settings import config
from .core.error_handlers import register_error_handlers
from .extensions import db, migrate
from .containers import Container

def create_app() -> Flask:
    app = Flask(__name__)


    # # Inicjalizacja kontenera DI


    container = Container()
    # To wdraza ustawienia z wiring_config w Container
    container.wire()
    #
    # Mozesz w razie czego potem w dowolnym miejscu do tego kontenera sie odwolac (np. w testach)
    # app.container = container
    #
    app.config.from_object(config['default'])
    config['default'].init_app(app)
    #
    register_error_handlers(app)
    app.register_blueprint(api_bp)
    #
    db.init_app(app)
    migrate.init_app(app, db)


    # Uruchamia "kontekst aplikacji" Flaska, co pozwala bezpiecznie korzystać z funkcji zależnych od aplikacji,
    # takich jak 'current_app' czy rozszerzenia (np. baza danych).
    with app.app_context():

        # Powoduje, że Python "odkrywa" wszystkie Twoje modele SQLAlchemy.
        # Jest to kluczowe, aby narzędzie do migracji (Flask-Migrate) wiedziało o tabelach, którymi ma zarządzać.
        from .database import models

        # Wypisuje do logów wartość klucza SECRET_KEY.
        # Służy to do sprawdzenia, czy konfiguracja została wczytana poprawnie.
        app.logger.info(f"SECRET KEY: {current_app.config['SECRET_KEY']}")

        # Loguje nazwę uruchomionej aplikacji Flaska.
        # Przydatne do debugowania i weryfikacji, która aplikacja jest uruchomiona.
        app.logger.info(f'WEB APP NAME: {current_app.name}')

        # Wyświetla w logach mapę wszystkich zarejestrowanych adresów URL (endpointów).
        # Pomaga sprawdzić, czy wszystkie widoki i blueprinty załadowały się poprawnie.
        app.logger.info(f'WEB APP ENDPOINTS: {current_app.url_map}')

        # Loguje listę wszystkich aktywnych rozszerzeń (extensions) w aplikacji.
        # Pozwala to potwierdzić, że np. SQLAlchemy czy Migrate zostały poprawnie zainicjalizowane.
        app.logger.info(f'WEB APP EXTENSTIONS: {current_app.extensions}')

    return app