from pydantic import BaseModel
from typing import Literal

from storage.webapp.services.deliveries.dtos import ReadInboundOrderProductDTO


# ------------------------------------------ Request Schema ------------------------------------------


class CreateInboundOrderSchema(BaseModel):
    warehouse_id: int
    supplier_id: int


class AddProductToInboundOrderSchema(BaseModel):
    order_id: int
    product_sku: str
    qty: int

class SetInboundOrderStatusSchema(BaseModel):
    order_id: int
    status: Literal["approved", "produced", "in_transit", "delivered", "completed", "cancelled"]

class UpdateQtySkuInboundOrderSchema(BaseModel):
    order_id: int
    sku: str
    qty: int


class DeleteInboundOrderSchema(BaseModel):
    inbound_order_id: int

class DeleteInboundOrderProductSchema(BaseModel):
    inbound_order_id: int
    product_sku: str


# ------------------------------------------ Response Schema ------------------------------------------

class InboundOrderResponseSchema(BaseModel):
    inbound_order_id: int
    warehouse_id: int
    supplier_id: int
    products: list[ReadInboundOrderProductDTO]
    status: Literal["approved", "produced", "in_transit", "delivered", "completed", "cancelled"]


class ReadInboundOrderProductsWithOrderSchema(BaseModel):
    warehouse_id: int
    inbound_order_id: int
    inbound_order_product_id: int
    product_id: int
    product_qty: int
    supplier_name: str
    status: str


