from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateInboundOrderDTO:
    warehouse_id: int
    supplier_id: int


@dataclass(frozen=True)
class AddProductToInboundOrderDTO:
    order_id: int
    product_sku: int
    qty: int



@dataclass(frozen=True)
class UpdateInboundOrderDTO:
    pass

@dataclass(frozen=True)
class ReadInboundOrderDTO:
    inbound_order_id: int
    warehouse_id: int
    supplier_id: int

@dataclass(frozen=True)
class ReadInboundOrderProductDTO:
    inbound_order_id: int
    product_id_sku: int
    quantity: int
    net_price: Decimal(10, 2)
    currency: str