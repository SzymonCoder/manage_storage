from .dtos import StockDTO, StockSummaryInboundUpdateDTO
from ....webapp.database.models.stocks_summary import StockSummary
from ....webapp.database.models.stocks_with_exp_dates import StockWithExpDate


def stock_to_dto(stock: list[StockSummary]) -> StockDTO:
    one = stock[0]
    return StockDTO(
        warehouse_id=one.warehouse_id,
        qty_total_of_sku=one.qty_total_of_sku,
        qty_added_products = len(stock)
    )


def stock_summary_inbound_update_to_dto(warehouse_id, sku_qty: int, qty: int) -> StockSummaryInboundUpdateDTO:
    return StockSummaryInboundUpdateDTO(
        warehouse_id = warehouse_id,
        updated_sku_qty = sku_qty,
        updated_qty = qty
    )