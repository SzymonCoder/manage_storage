from logging.config import dictConfig
from dotenv import load_dotenv
from flask import Flask
from urllib.parse import quote_plus
import os

load_dotenv()


class Config:
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'default secret key')
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False') in ('1', 'true', 'True')
    TESTING: bool = False

    # ------------------------------------------------------------------------------------------------------------------
    # Zmienne środowiskowe od bazy danych
    # ------------------------------------------------------------------------------------------------------------------

    MYSQL_DIALECT: str = os.getenv('MYSQL_DIALECT', 'mysql+mysqldb')
    MYSQL_HOST: str = os.getenv('MYSQL_HOST', 'mysql')
    MYSQL_DATABASE: str = os.getenv('MYSQL_DATABASE', 'db_orders')
    MYSQL_USER: str = os.getenv('MYSQL_USER', 'user')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD', 'user1234')
    MYSQL_ROOT_PASSWORD: str = os.getenv('MYSQL_ROOT_PASSWORD', 'root')
    MYSQL_PORT: str = os.getenv('MYSQL_PORT', '3307')

    # ------------------------------------------------------------------------------------------------------------------
    # SQLALCHEMY DATABASE URI
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"{self.MYSQL_DIALECT}://{self.MYSQL_USER}:{quote_plus(self.MYSQL_PASSWORD)}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )

    """
    To jest flask-sqlalchemy-specific opcja, nie SQLAlchemy core.
    Domyślnie (w starszych wersjach) była True, co powodowało:
    ->  Flask-SQLAlchemy śledził zmiany w obiektach (w modelach), żeby móc emitować sygnały (signals).
    -> Bylo to kosztowne dla RAM i CPU
    Większość projektów tego nie używa, więc ustawienie False jest zalecaną praktyką.
    Dzięki temu wyłączasz dodatkowe „trackowanie zmian” i dostajesz czystsze logi (bez ostrzeżeń).
    Zawsze ustawiaj False, chyba że naprawdę używasz signals (99% projektów nie używa).
    """
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    """
    To jest słownik przekazywany prosto do SQLAlchemy.create_engine(), czyli wszystkie parametry dotyczące 
    connection pool (puli połączeń do DB).

    ->  pool_pre_ping: True
    Włącza testowanie połączenia przed jego użyciem (małe SELECT 1 w tle).
    Rozwiązuje problem „MySQL server has gone away”, gdy połączenie w puli zdążyło się rozłączyć (np. DB zamknęła 
    socket po idle).  Bez tego: pierwsze zapytanie po dłuższej przerwie może wyrzucić błąd.

    ->  pool_recycle: 1800
    Po tylu sekundach (1800 = 30 minut) SQLAlchemy zamyka i otwiera połączenie na nowo.
    Chroni przed sytuacją, gdy serwer MySQL sam zamyka połączenia po wait_timeout.
    Warto ustawić zawsze na wartość mniejszą niż wait_timeout w MySQL (domyślnie 28800s = 8h, ale w hostingach/Cloud bywa 
    krócej, np. 1h).

    ->  pool_size: 10
    Ile stałych połączeń trzyma pula (maksymalnie „rozgrzanych” i gotowych).
    To Twoje bazowe minimum.
    Jeśli masz 10 workerów w Gunicorn, to typowo ustawiasz pool_size >= workers.

    ->  max_overflow: 20
    Dodatkowe połączenia, które pula może otworzyć ponad pool_size, jeśli wszystkie są zajęte.
    Czyli: max aktywnych połączeń = pool_size + max_overflow.
    W Twoim przypadku: 10 + 20 = 30.

    Jak to dziala razem?
    ->  normalnie masz 10 połączeń trzymanych w puli,
    ->  jak ruch skoczy, pula może tymczasowo otworzyć dodatkowe 20 (razem 30),
    ->  każde połączenie jest sprawdzane przed użyciem (pool_pre_ping),
    ->  co max 30 minut recyklujesz sockety (pool_recycle).
    """
    SQLALCHEMY_ENGINE_OPTIONS: dict[str, bool | int] = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 10,
        "max_overflow": 20,
    }

    @classmethod
    def init_app(cls, app: Flask) -> None:
        # --------------------------------------------------------------------------------------------------------------
        # Konfiguracja loggerow
        # --------------------------------------------------------------------------------------------------------------
        #cls.configure_logging(app)

        # --------------------------------------------------------------------------------------------------------------
        # Teraz bedziemy wstrzykiwac konfiguracje dla bazy danych
        # --------------------------------------------------------------------------------------------------------------
        conf = cls()
        app.config['SQLALCHEMY_DATABASE_URI'] = conf.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cls.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = cls.SQLALCHEMY_ENGINE_OPTIONS

        app.logger.debug('Logger initialized')


config: dict[str, type[Config]] = {
    'default': Config,
}

