from .dtos import StockDTO, StockSummaryInboundUpdateDTO, ReadStockExpDateDTO
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

# TODO: trzeba zrobic transfer statusow z klasy na napis

def to_dto_read_stock_with_exp_date(stock: StockWithExpDate) -> ReadStockExpDateDTO:
    return ReadStockExpDateDTO(
        warehouse_id=stock.warehouse_id,
        product_id=stock.product_id,
        expiration_date=stock.expiration_date,
        qty_per_exp_date=stock.qty_per_exp_date,
        qty_total_of_sku=stock.qty_total_of_sku,
        status_of_exp_date=stock.status_of_exp_date,
        status_of_total_qty=stock.status_of_total_qty
    )