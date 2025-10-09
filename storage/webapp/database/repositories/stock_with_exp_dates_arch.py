from sqlalchemy import select
from ..models.stocks_with_exp_dates_arch import StockWithExpDateArch
from ...extensions import db
from .generic import GenericRepository

class StockWithExpDateArchRepository(GenericRepository[StockWithExpDateArch]):
    def __init__(self):
        super().__init__(StockWithExpDateArch)