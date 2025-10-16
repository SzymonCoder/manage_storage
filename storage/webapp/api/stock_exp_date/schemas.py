from pydantic import BaseModel
from datetime import datetime
from typing import Literal



class ReadStockExpDateSchema(BaseModel):
    warehouse_id: int
    product_id: int
    expiration_date: datetime
    qty_per_exp_date: int
    qty_total_of_sku: int
    status_of_exp_date: str
    status_of_total_qty: str