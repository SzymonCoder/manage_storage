from pydantic import BaseModel
from datetime import datetime
from typing import Literal



class ReadStockExpDateSchema(BaseModel):
    warehouse_id: int
    product_id: int
    expiration_date: datetime
    qty_per_exp_date: int
    qty_total_of_sku: int
    status_of_exp_date: Literal["good_date", "medium_date", "critical_date", "expired", "no_products", "not_apply"]
    status_of_total_qty: Literal["good_qty", "medium_qty", "critical_qty", "too_low_qty", "no_products"]