from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

@dataclass(frozen=True)
class CreateInboundOrderDTO:
    warehouse_id: int
    supplier_id: int


@dataclass(frozen=True)
class AddProductToInboundOrderDTO:
    order_id: int
    product_sku: str
    qty: int



@dataclass(frozen=True)
class UpdateQtySkuInboundOrderDTO:
    order_id: int
    sku: str
    qty: int



@dataclass(frozen=True)
class ReadInboundOrderDTO:
    inbound_order_id: int
    warehouse_id: int
    supplier_id: int


@dataclass(frozen=True)
class SetInboundOrderStatusDTO:
    order_id: int
    status: Literal["approved", "produced", "in_transit", "delivered", "completed", "cancelled"]


@dataclass(frozen=True)
class ReadInboundOrderProductDTO:
    inbound_order_id: int
    product_id_sku: int
    quantity: int
    net_price: Decimal(10, 2)
    currency: str


@dataclass(frozen=True)
class CreateOrderProductDTO:
    product_sku: str
    quantity: int

@dataclass(frozen=True)
class DeleteInboundOrderDTO:
    inbound_order_id: int

@dataclass(frozen=True)
class DeleteInboundOrderProductDTO:
    inbound_order_id: int
    product_sku: str