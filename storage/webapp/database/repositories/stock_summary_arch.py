from sqlalchemy import select, func

from ..models.products import Product
from ..models.stocks_summary_arch import StockSummaryArch
from ...extensions import db
from .generic import GenericRepository

class StockSummaryArchRepository(GenericRepository[StockSummaryArch]):
    def __init__(self):
        super().__init__(StockSummaryArch)