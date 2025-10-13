from typing import Literal, Annotated
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime








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
