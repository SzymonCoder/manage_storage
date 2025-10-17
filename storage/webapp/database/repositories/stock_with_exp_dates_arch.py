from ..models.stocks_with_exp_dates_arch import StockWithExpDateArch
from ..models.stocks_with_exp_dates_arch import StockWithExpDateArch
from ..repositories.generic import GenericRepository


class StockWithExpDateArchRepository(GenericRepository[StockWithExpDateArch]):
    def __init__(self):
        super().__init__(StockWithExpDateArch)