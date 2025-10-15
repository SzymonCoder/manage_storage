from .dtos import ReadInboundOrderDTO, ReadInboundOrderProductsWithOrderDTO
from webapp.database.models.inbound_orders import InboundOrder



def inbound_order_to_dto(order: InboundOrder) -> ReadInboundOrderDTO:
    return ReadInboundOrderDTO(
        inbound_order_id=order.id,
        warehouse_id=order.warehouse_id,
        supplier_id=order.supplier_id,
        products=list(order.products),
        status=order.status
    )

def inbound_orders_with_products_to_dto(orders: list[dict]) -> list[ReadInboundOrderProductsWithOrderDTO]:
    results = []
    for order in orders:
        results.append(
            ReadInboundOrderProductsWithOrderDTO(
                warehouse_id=order["warehouse_id"],
                inbound_order_id=order["inbound_order_id"],
                inbound_order_product_id=order["inbound_order_product_id"],
                product_id=order["product_id"],
                product_qty=order["product_qty"],
                supplier_name=order["supplier_name"],
                status=order["status"]
            )
        )
    return results
