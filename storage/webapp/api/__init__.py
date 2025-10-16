from flask import Blueprint

# Importuj blueprinty z poszczególnych modułów
from .stock_summary.routers import stock_summary_bp
from .stock_exp_date.routes import stock_exp_date_bp
from .deliveries.routers import order_inbound_bp
# ... inne importy, jeśli istnieją

# Stwórz główny blueprint dla całego API z prefiksem /api
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Zarejestruj pod-blueprinty z ich własnymi prefiksami
api_bp.register_blueprint(stock_summary_bp, url_prefix='/stock_summary')
api_bp.register_blueprint(stock_exp_date_bp, url_prefix='/stock_exp_date')
api_bp.register_blueprint(order_inbound_bp, url_prefix='/order_inbound')
# ... inne rejestracjedate')