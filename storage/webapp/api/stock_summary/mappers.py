from ....webapp.api.stock_summary.schemas import StockResponseSchema
from ....webapp.services.stock.dtos import StockSummaryDTO





def to_schema_read_summary_stock(stocks_dto: list[StockSummaryDTO]) -> list[StockResponseSchema] | None:

    response_stock: list[StockResponseSchema] = []

    for stock_dto in stocks_dto:

        response_stock.append(
            StockResponseSchema(
            warehouse_id=stock_dto.warehouse_id,
            product_id=stock_dto.product_id,
            good_date_qty=stock_dto.good_date_qty,
            medium_date_qty=stock_dto.medium_date_qty,
            critical_date_qty=stock_dto.critical_date_qty,
            expired_qty=stock_dto.expired_qty,
            qty_total_of_sku=stock_dto.qty_total_of_sku,
            ordered_in_qty=stock_dto.ordered_in_qty,
            status_of_total_qty=stock_dto.status_of_total_qty,
            created_at=stock_dto.created_at
            )
        )

    return response_stock
