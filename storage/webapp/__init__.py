import os

from flask import current_app, send_from_directory, Flask

from . import database
from .api import api_bp
from .containers import Container
from .core.error_handlers import register_error_handlers
from .extensions import db, migrate
from .settings import config


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

    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

    print(f"Frontend directory: {frontend_dir}")
    print(f"Index.html exists: {os.path.exists(os.path.join(frontend_dir, 'index.html'))}")

    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filename>')
    def static_pages(filename):
        # Nie obsługuj endpointów API
        if filename.startswith('api/'):
            from flask import abort
            abort(404)
        return send_from_directory(frontend_dir, filename)


    # Uruchamia "kontekst aplikacji" Flaska, co pozwala bezpiecznie korzystać z funkcji zależnych od aplikacji,
    # takich jak 'current_app' czy rozszerzenia (np. baza danych).
    with app.app_context():

        # Powoduje, że Python "odkrywa" wszystkie Twoje modele SQLAlchemy.
        # Jest to kluczowe, aby narzędzie do migracji (Flask-Migrate) wiedziało o tabelach, którymi ma zarządzać.
        from webapp.database import models

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