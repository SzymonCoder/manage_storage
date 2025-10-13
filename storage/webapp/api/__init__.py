from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# TO WAZNE zeby importowanie ten Blueprint dopiero jak masz api_bb
from .stock_summary import stock_summary_bp
api_bp.register_blueprint(stock_summary_bp)