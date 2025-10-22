
#ustwia bazowy obraz docker jaki mjest python slim (mniejsza wersja pythona)
FROM python:3.13-slim


#nie tworzy plików .pyc (bytecode)
#wyświetla printy w consoli bez opóźnień
#lokalizacja instalacji Poetry (menedżera pakietów)
#dodaje folder Poetry do ścieżki systemowej, żeby móc używać polecenia poetry w terminalu

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

#   Instaluje potrzebne narzędzia systemowe i biblioteki C, a potem czyści cache.
#	    Dlaczego:
#	        > procps → narzędzia do monitorowania procesów (ps, top).
#	        > build-essential → podstawowe narzędzia do kompilowania pakietów C.
#	        > curl → do pobierania plików z internetu (np. instalatora Poetry).
#	        > gcc, python3-dev → kompilator i nagłówki Pythona do instalowania pakietów, które mają komponenty C.
#	        > default-libmysqlclient-dev, libpq-dev → biblioteki do obsługi MySQL i PostgreSQL.
#	        > pkg-config → pomaga przy instalacji bibliotek.
#	        > rm -rf /var/lib/apt/lists/* → czyści listy pakietów, żeby obraz był mniejszy.

RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    build-essential \
    curl \
    gcc \
    python3-dev\
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config\
    && rm -rf /var/lib/apt/lists/*


#	Co robi: \
#       > Pobiera i instaluje Poetry (menedżer pakietów Pythona).
#	    > -sSL → cicho, bez pokazywania progresu, z przekierowaniem SSL.
#	    > | python3 → wynik pobrania od razu uruchamia Pythonem.

RUN curl -sSL https://install.python-poetry.org | python3


# Ustawia katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiuje pliki konfiguracyjne Poetry do kontenera. Potrzebne po to by Docker mógł zbudować szybko obraz
COPY pyproject.toml poetry.lock* ./

# Instaluje wszystkie zależności projektu w systemoym Pythonie kontenera (bez wirtualnego środowiska)
# Only mian -> bez pakeitu dev
# --no-interaction --no-ansi --no-root → ciche, bez kolorów i bez instalowania samego projektu jako pakietu

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root


# Kopiuje resztę plików projektu do kontenera (. = katalog lokalny, . = katalog w kontenerze /app)
COPY . .

# Informuje (nie otweira portu), ze kontener bedzie nasluchiwal na tym porcie
EXPOSE 5000

# Uruchamia komendy zapisane w CMD po uruchomieniu kontenera
#	1.	gunicorn → serwer aplikacji Flask/Django
#	2.	--bind 0.0.0.0:5000 → nasłuchuje na wszystkich interfejsach i porcie 5000
#	3.	--workers 1 → liczba procesów obsługujących żądania
#	4.	--reload → automatycznie przeładowuje przy zmianie kodu (tylko dev)
#	5.	app:app → plik:obiekt Flask (np. app.py i app = Flask(__name__))

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--reload", "app:app"]