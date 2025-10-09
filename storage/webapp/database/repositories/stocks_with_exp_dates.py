from sqlalchemy import select, delete
from ...extensions import db
from ..models.stocks_with_exp_dates import StockWithExpDate
from ..models.stocks_with_exp_dates_arch import StockWithExpDateArch
from .generic import GenericRepository


class StocksWithExpDateRepository(GenericRepository[StockWithExpDate]):
    def __init__(self, arch_repo: StockWithExpDateArch):
        super().__init__(StockWithExpDate)
        self.arch_repo = arch_repo

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

    def transfer_to_archive(self, warehouse_id: int) -> None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.warehouse_id.is_(warehouse_id))
        data_to_archive: list[StockWithExpDate] = list(db.session.scalars(stmt))

        if not data_to_archive:
            return
        new_archive_models = [
            StockWithExpDateArch(
                warehouse_id=rec.warehouse_id,
                product_id=rec.product_id,
                good_date_qty=rec.good_date_qty,
                medium_date_qty=rec.medium_date_qty,
                critical_date_qty=rec.critical_date_qty,
                expired_qty=rec.expired_qty,
                qty_total_of_sku=rec.qty_total_of_sku,
                ordered_in_qty=rec.ordered_in_qty,
                status_of_total_qty=rec.status_of_total_qty,
                created_at=rec.created_at,
                updated_at=rec.updated_at
            ) for rec in data_to_archive
        ]

        self.arch_repo.add_many(new_archive_models)

        delete_stmt = delete(StockWithExpDate).where(StockWithExpDate.id.in_([rec.id for rec in new_archive_models]))
        db.session.execute(delete_stmt)



    # TODO: Repository stocks_with_exp_dates oraz stocks_summary maja kilka podobnych filtrów, więc warto
    # TODO: pochylić się nad tym i zrobic klasę abstrakcyjną, po ktorej będa również dziedziczyć tak by
    # TODO: uniknąć DRY

