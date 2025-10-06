from webapp import create_app

import sys
import os

# Dodaj główny katalog aplikacji do ścieżki Pythona
# To zapewnia, że moduły takie jak 'webapp' będą zawsze znajdowane.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))




app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')