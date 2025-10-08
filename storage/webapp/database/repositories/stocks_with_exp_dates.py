from sqlalchemy import select
from ...extensions import db
from ..models.stocks_with_exp_dates import StockWithExpDate
from .generic import GenericRepository


class StocksWithExpDateRepository(GenericRepository[StockWithExpDate]):
    def __init__(self):
        super().__init__(StockWithExpDate)

# ------------------------ Aktualizacje statusow i opisu ------------------------

    def set_exp_date_status(self, status: StockWithExpDate.status_of_exp_date) -> None:
        self.model.status_of_total_qty = status

    def set_total_qty_status(self, status: StockWithExpDate.status_of_total_qty) -> None:
        self.model.status_of_exp_date = status


# ------------------------ Filtry ------------------------

    def get_by_sku(self, sku: str) -> list[StockWithExpDate] | None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.sku.is_(sku))
        return list(db.session.scalar(stmt))


    def get_by_qty_status(self, status: StockWithExpDate.status_of_total_qty) -> list[StockWithExpDate] | None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.status_of_total_qty.is_(status))
        return list(db.session.scalar(stmt))

    def get_by_warehouse_id(self, warehouse_id: int) -> list[StockWithExpDate] | None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.warehouse_id.is_(warehouse_id))
        return list(db.session.scalar(stmt))

    def get_by_exp_date_status(self, status: StockWithExpDate.status_of_exp_date) -> list[StockWithExpDate] | None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.status_of_exp_date.is_(status))
        return list(db.session.scalar(stmt))

    # TODO: Repository stocks_with_exp_dates oraz stocks_summary maja kilka podobnych filtrów, więc warto
    # TODO: pochylić się nad tym i zrobic klasę abstrakcyjną, po ktorej będa również dziedziczyć tak by
    # TODO: uniknąć DRY

