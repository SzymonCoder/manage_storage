from sqlalchemy import select, delete

from .stock_summary_arch import StockSummaryArchRepository
from ...extensions import db
from ..models.stocks_summary import StockSummary
from ..models.stocks_summary_arch import StockSummaryArch
from .generic import GenericRepository


class StockSummaryRepository(GenericRepository[StockSummary]):
    def __init__(self, arch_repo: StockSummaryArchRepository):
        super().__init__(StockSummary)
        self.arch_repo = arch_repo


# ------------------------ Aktualizacje statusow i opisu ------------------------

    def set_qty_in_column(self, qty: int, column_name: str) -> None:
         setattr(self.model, column_name, qty)

    def set_qty_status(self, status: StockSummary.status_of_total_qty) -> None:
        self.model.status_of_total_qty = status


# ------------------------ Filtry ------------------------

    def get_all(self) -> list[StockSummary] | None:
        stmt = select(StockSummary)
        result = list(db.session.scalars(stmt))
        print(f"Fetched stocks: {result}")
        return result

        # return list(db.session.scalars(stmt))

    def get_by_sku(self, sku: str) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.sku.is_(sku))
        return list(db.session.scalar(stmt))

    def get_by_expired_qty(self) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.expired_qty.isnot(None))
        return list(db.session.scalar(stmt))

    def get_by_qty_status(self, status: StockSummary.status_of_total_qty, warehouse_id: int | None) -> list[StockSummary] | None:
        if not warehouse_id:
            stmt = select(StockSummary).where(StockSummary.status_of_total_qty.is_(status))
        else:
            stmt = select(StockSummary).where(StockSummary.warehouse_id.is_(warehouse_id)).where(StockSummary.status_of_total_qty.is_(status))
        return list(db.session.scalars(stmt))

    def get_by_warehouse_id(self, warehouse_id: int) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.warehouse_id.is_(warehouse_id))
        return list(db.session.scalar(stmt))


    def get_by_warehouse_id_and_sku(self, warehouse_id: int, sku: str) -> StockSummary | None:
        stmt = select(StockSummary).where(StockSummary.warehouse_id.is_(warehouse_id)).where(StockSummary.sku.is_(sku))
        return db.session.scalar(stmt)


    def transfer_to_archive(self, warehouse_id: int) -> None:
        stmt = select(StockSummary).where(StockSummary.warehouse_id.is_(warehouse_id))
        data_to_archive: list[StockSummary] = list(db.session.scalars(stmt))

        if not data_to_archive:
            return
        new_archive_models = [
            StockSummaryArch(
                warehouse_id = rec.warehouse_id,
                product_id = rec.product_id,
                good_date_qty = rec.good_date_qty,
                medium_date_qty = rec.medium_date_qty,
                critical_date_qty = rec.critical_date_qty,
                expired_qty = rec.expired_qty,
                qty_total_of_sku = rec.qty_total_of_sku,
                ordered_in_qty = rec.ordered_in_qty,
                status_of_total_qty = rec.status_of_total_qty,
                created_at = rec.created_at,
                updated_at = rec.updated_at
            ) for rec in data_to_archive
        ]

        self.arch_repo.add_many(new_archive_models)

        delete_stmt = delete(StockSummary).where(StockSummary.id.in_([rec.id for rec in new_archive_models]))
        db.session.execute(delete_stmt)

