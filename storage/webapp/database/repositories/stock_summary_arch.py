from .generic import GenericRepository
from ..models.stocks_summary_arch import StockSummaryArch


class StockSummaryArchRepository(GenericRepository[StockSummaryArch]):
    def __init__(self):
        super().__init__(StockSummaryArch)