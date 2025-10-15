from ...database.models.stocks_summary import StockSummary
from webapp.api.stock_summary.schemas import (
    StockResponseSchema,
    StockUpdateResponseSchema,
    StockUpdateResponseSchema,
    StockUpdateInboundQtyResponseSchema
)
from webapp.services.stock.dtos import StockSummaryDTO, StockSummaryInboundUpdateDTO






def to_schema_read_summary_stock(dto: StockSummaryDTO) -> StockResponseSchema | None:
    return StockResponseSchema(
        warehouse_id=dto.warehouse_id,
        product_id=dto.product_id,
        good_date_qty=dto.good_date_qty,
        medium_date_qty=dto.medium_date_qty,
        critical_date_qty=dto.critical_date_qty,
        expired_qty=dto.expired_qty,
        qty_total_of_sku=dto.qty_total_of_sku,
        ordered_in_qty=dto.ordered_in_qty,
        status_of_total_qty=dto.status_of_total_qty,
        created_at=dto.created_at
        )




def to_schema_stock_update_response(stock: list[StockSummary]) -> StockUpdateResponseSchema:
    return StockUpdateResponseSchema(
        warehouse_id=stock[0].warehouse_id,
        rows_number=len(stock)
    )

def to_schema_dto_inb_qty_update(dto: StockSummaryInboundUpdateDTO) -> StockUpdateInboundQtyResponseSchema:
    return StockUpdateInboundQtyResponseSchema(
        warehouse_id=dto.warehouse_id,
        updated_sku_qty=dto.updated_sku_qty,
        updated_qty=dto.updated_qty
    )