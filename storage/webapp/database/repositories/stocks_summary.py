from sqlalchemy import select
from ...extensions import db
from ..models.stocks_summary import StockSummary
from .generic import GenericRepository


class StockSummaryRepository(GenericRepository[StockSummary]):
    def __init__(self):
        super().__init__(StockSummary)


# ------------------------ Aktualizacje statusow i opisu ------------------------

    def set_qty_in_column(self, qty: int, column_name: str) -> None:
         setattr(self.model, column_name, qty)

    def set_qty_status(self, status: StockSummary.status_of_total_qty) -> None:
        self.model.status_of_total_qty = status


# ------------------------ Filtry ------------------------

    def get_by_sku(self, sku: str) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.sku.is_(sku))
        return list(db.session.scalar(stmt))

    def get_by_expired_qty(self) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.expired_qty.isnot(None))
        return list(db.session.scalar(stmt))

    def get_by_qty_status(self, status: StockSummary.status_of_total_qty) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.status_of_total_qty.is_(status))
        return list(db.session.scalar(stmt))

    def get_by_warehouse_id(self, warehouse_id: int) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.warehouse_id.is_(warehouse_id))
        return list(db.session.scalar(stmt))
