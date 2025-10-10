from .dtos import ReadInboundOrderDTO
from ....webapp.database.models.inbound_orders import InboundOrder



def inbound_order_to_dto(order: InboundOrder) -> ReadInboundOrderDTO:
    return ReadInboundOrderDTO(
        inbound_order_id=order.id,
        warehouse_id=order.warehouse_id,
        supplier_id=order.supplier_id
    )