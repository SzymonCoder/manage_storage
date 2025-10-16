from sqlalchemy import select, delete
from ...extensions import db
from ..models.stocks_with_exp_dates import StockWithExpDate, StockQtyStatus, ExpDateStatus
from ..models.stocks_with_exp_dates_arch import StockWithExpDateArch
from .generic import GenericRepository


class StocksWithExpDateRepository(GenericRepository[StockWithExpDate]):
    def __init__(self, arch_repo: StockWithExpDateArch):
        super().__init__(StockWithExpDate)
        self.arch_repo = arch_repo



# ------------------------ Filtry ------------------------

    def get_by_sku(self, sku: str) -> list[StockWithExpDate] | None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.sku.is_(sku))
        return list(db.session.scalars(stmt))


    def get_by_qty_status(self, status: str) -> list[StockWithExpDate] | None:
        converted_status = self._map_qty_status(status)
        stmt = select(StockWithExpDate).where(StockWithExpDate.status_of_total_qty.is_(converted_status))
        return list(db.session.scalars(stmt))

    def get_by_warehouse_id(self, warehouse_id: int) -> list[StockWithExpDate] | None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.warehouse_id == warehouse_id)
        return list(db.session.scalars(stmt))

    def get_by_exp_date_status(self, status: str) -> list[StockWithExpDate] | None:
        converted_status = self._map_exp_date_status(status)
        stmt = select(StockWithExpDate).where(StockWithExpDate.status_of_exp_date == converted_status)
        return list(db.session.scalars(stmt))

    def transfer_to_archive(self, warehouse_id: int) -> None:
        stmt = select(StockWithExpDate).where(StockWithExpDate.warehouse_id == warehouse_id)
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



    # TODO: pochylić się nad tym i zrobic klasę abstrakcyjną, po ktorej będa również dziedziczyć tak by
    # TODO: uniknąć DRY


# ------------------------ Aktualizacje statusow i opisu ------------------------

    def _set_exp_date_status(self, obj: StockWithExpDate, status: str) -> None:
        obj.status_of_exp_date = self._map_exp_date_status(status)


    def _set_total_qty_status(self, obj: StockWithExpDate, status: str) -> None:
        obj.status_of_total_qty = self._map_qty_status(status)



    def _map_qty_status(self, status: str) -> StockQtyStatus:
        try:
            return StockQtyStatus(status)
        except ValueError:
            # Obsłuż sytuację, gdy string nie pasuje do żadnego statusu
            raise ValueError(f"'{status}' is not a valid stock status.")

    def _map_exp_date_status(self, status: str) -> ExpDateStatus:
        try:
            return ExpDateStatus(status)
        except ValueError:
            # Obsłuż sytuację, gdy string nie pasuje do żadnego statusu
            raise ValueError(f"'{status}' is not a valid stock status.")
