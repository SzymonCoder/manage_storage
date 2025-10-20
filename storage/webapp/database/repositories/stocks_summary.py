from sqlalchemy import select, delete

from .generic import GenericRepository
from .stock_summary_arch import StockSummaryArchRepository
from ..models.products import Product
from ..models.stocks_summary import StockSummary
from ..models.stocks_summary_arch import StockSummaryArch
from ..models.stocks_with_exp_dates import StockQtyStatus
from ...extensions import db
from ...services.extension import ValidationException


class StockSummaryRepository(GenericRepository[StockSummary]):
    def __init__(self, arch_repo: StockSummaryArchRepository):
        super().__init__(StockSummary)
        self.arch_repo = arch_repo


# ------------------------ Aktualizacje statusow i opisu ------------------------

    def set_qty_in_column(self, qty: int, column_name: str) -> None:
         setattr(self.model, column_name, qty)

    def set_qty_status(self, obj: StockSummary, status: str) -> None:
        obj.status_of_total_qty = self._map_qty_status(status)



# ------------------------ Filtry ------------------------

    # takie samo w GenericRepository
    # def get_all(self) -> list[StockSummary]:
    #     stmt = select(StockSummary)
    #     result = list(db.session.scalars(stmt))
    #     print(f"Fetched stocks: {result}")
    #     return result

        # return list(db.session.scalars(stmt))

    def get_by_sku(self, sku: str) -> list[StockSummary] | None:
        stmt = select(StockSummary).join(Product, Product.id == StockSummary.product_id).where(Product.sku == sku)
        return list(db.session.scalar(stmt))

    def get_by_expired_qty(self) -> list[StockSummary] | None:
        stmt = select(StockSummary).where(StockSummary.expired_qty.isnot(None))
        return list(db.session.scalar(stmt))

    def get_by_qty_status(self, status: str, warehouse_id: int | None) -> list[StockSummary] | None:
        mapped_status = self._map_qty_status(status)
        if not warehouse_id:
            stmt = select(StockSummary).where(StockSummary.status_of_total_qty == mapped_status)
        else:
            stmt = (select(StockSummary)
                    .where(StockSummary.warehouse_id == warehouse_id)
                    .where(StockSummary.status_of_total_qty == mapped_status))

        return list(db.session.scalars(stmt))

    def get_by_warehouse_id(self, warehouse_id: int) -> list[StockSummary]:
        stmt = select(StockSummary).where(StockSummary.warehouse_id == warehouse_id)
        return list(db.session.scalars(stmt))


    def get_by_warehouse_id_and_product_sku(self, warehouse_id: int, sku: str) -> StockSummary | None:
        stmt = (
            select(StockSummary)
            .join(StockSummary.product)  # ORM-owy join
            .where(
                StockSummary.warehouse_id == warehouse_id,
                Product.sku == sku
            )
        )
        return db.session.scalar(stmt)


    def transfer_to_archive(self, warehouse_id: int) -> None:
        stmt = select(StockSummary).where(StockSummary.warehouse_id == warehouse_id)
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
        self.delete_all()




    def _map_qty_status(self, status: str) -> StockQtyStatus:
        try:
            return StockQtyStatus(status)
        except ValueError:
            raise ValidationException(f'Invalid status {status}')