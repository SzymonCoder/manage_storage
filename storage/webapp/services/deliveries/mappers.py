from itertools import product

from webapp.database.models.inbound_orders import InboundOrder

from .dtos import ReadInboundOrderDTO, ReadInboundOrderProductsWithOrderDTO, ReadInboundOrderProductDTO


def inbound_order_to_dto(order: InboundOrder) -> ReadInboundOrderDTO:
    return ReadInboundOrderDTO(
        inbound_order_id=order.id,
        warehouse_id=order.warehouse_id,
        supplier_id=order.supplier_id,
        status=order.status.value
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



# def inbound_orders_to_dto(orders: list[dict]) -> list[ReadInboundOrderProductsWithOrderDTO]:
#     """
#     Mapuje listę słowników (wynik zapytania SQLAlchemy) na listę DTO ReadInboundOrderProductsWithOrderDTO.
#     Zamówienia bez produktów również są uwzględnione, products będą puste.
#     """
#     results = []
#     for order in orders:
#         # Jeśli chcesz, możesz w tym miejscu rozpakować produkty jako listę DTO wewnątrz ReadInboundOrderProductsWithOrderDTO
#         # Ale na podstawie Twojego DTO zakładam, że każde DTO reprezentuje jeden produkt w zamówieniu
#         results.append(
#             ReadInboundOrderProductsWithOrderDTO(
#                 warehouse_id=order["warehouse_id"],
#                 inbound_order_id=order["inbound_order_id"],
#                 inbound_order_product_id=order.get("inbound_order_product_id"),
#                 product_id=order.get("product_id"),
#                 product_qty=order.get("product_qty"),
#                 supplier_name=order["supplier_name"],
#                 status=order["status"]
#             )
#         )
#     return results


def inbound_orders_to_dto(orders: list[dict]) -> list[ReadInboundOrderProductsWithOrderDTO]:
    result = []

    for order in orders:
        result.append(ReadInboundOrderProductsWithOrderDTO(
            inbound_order_id=order["inbound_order_id"],
            warehouse_id=order["warehouse_id"],
            supplier_name=order.get("supplier_name"),
            status=order["status"],
            products=[
                ReadInboundOrderProductInfoDTO(
                    inbound_order_product_id=prod["inbound_order_product_id"],
                    product_id=prod["product_id"],
                    product_qty=prod["product_qty"],
                    sku=prod.get("sku")
                ) for prod in (order.get("products") or [])
            ]
        ))
    return result