from pydantic import BaseModel
from datetime import datetime






# ------------------------------------------ Response Schema ------------------------------------------

class StockResponseSchema(BaseModel):
    warehouse_id: int
    product_id: int
    good_date_qty: int
    medium_date_qty: int
    critical_date_qty: int
    expired_qty: int
    qty_total_of_sku: int
    ordered_in_qty: int
    status_of_total_qty: str
    created_at: datetime


class StockUpdateResponseSchema(BaseModel):
    warehouse_id: int
    rows_number: int


class StockUpdateInboundQtyResponseSchema(BaseModel):
    warehouse_id: int
    updated_sku_qty: int
    updated_qty: int
