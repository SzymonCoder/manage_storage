from flask import request, jsonify
from flask.typing import ResponseReturnValue
from dependency_injector.wiring import inject, Provide

from .mappers import (
    to_dto_order_inbound,
    to_schema_dto_order_inbound,
    to_dto_add_product_to_order,
    to_dto_update_status_order,
    to_dto_update_qty_sku,
    to_dto_delete_order,
    to_dto_delete_order_product,
    to_schema_dto_inbound_order_with_products
)

from webapp.api.deliveries.schemas import (
    CreateInboundOrderSchema,
    AddProductToInboundOrderSchema,
    SetInboundOrderStatusSchema,
    UpdateQtySkuInboundOrderSchema,
    DeleteInboundOrderSchema,
    DeleteInboundOrderProductSchema
)



from webapp.services.deliveries.services import InboundOrderService


from webapp.containers import Container
from . import order_inbound_bp
from ...database.models.inbound_orders import InboundOrderStatus
from ...services.deliveries.dtos import ReadInboundOrderProductsWithOrderDTO


# ----------------------------------------- Create / Modify Order Inbound -----------------------------------------

@order_inbound_bp.post("/create_order")
@inject
def create_order(inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service]) -> ResponseReturnValue:
    payload = CreateInboundOrderSchema.model_validate(request.get_json() or {})
    dto = to_dto_order_inbound(payload)
    read_dto = inbound_order_service.add_inbound_order(dto)
    return jsonify(to_schema_dto_order_inbound(read_dto).model_dump(mode='json')), 201


@order_inbound_bp.post("/add_product_to_order")
@inject
def add_product_to_order(
        inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service],
    ) -> ResponseReturnValue:
    payload = AddProductToInboundOrderSchema.model_validate(request.get_json() or {})
    dto = to_dto_add_product_to_order(payload)
    read_dto = inbound_order_service.add_product_to_inbound_order(dto)
    return jsonify(to_schema_dto_order_inbound(read_dto).model_dump(mode='json')), 201


@order_inbound_bp.patch("/update_product_status_in_order")
@inject
def update_order_inbound_status(
        inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service]
) -> ResponseReturnValue:
    payload = SetInboundOrderStatusSchema.model_validate(request.get_json() or {})
    dto = to_dto_update_status_order(payload)
    read_dto = inbound_order_service.set_status(dto)
    return jsonify(to_schema_dto_order_inbound(read_dto).model_dump(mode='json')), 200


@order_inbound_bp.patch("/update_qty_sku_in_order")
@inject
def update_qty_sku_in_order(
        inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service]
) -> ResponseReturnValue:
    payload = UpdateQtySkuInboundOrderSchema.model_validate(request.get_json() or {})
    dto = to_dto_update_qty_sku(payload)
    read_dto = inbound_order_service.update_qty(dto)
    return jsonify(to_schema_dto_order_inbound(read_dto).model_dump(mode='json')), 200


@order_inbound_bp.delete("/delete_order/<int:inbound_order_id>")
@inject
def delete_order(
        inbound_order_id: int,
        inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service],
) -> ResponseReturnValue:
    schema = DeleteInboundOrderSchema(inbound_order_id=inbound_order_id)
    dto = to_dto_delete_order(schema)
    inbound_order_service.delete_order(dto)
    return jsonify({"message": f"Order {inbound_order_id} deleted successfully"}), 200


@order_inbound_bp.delete("/delete_product_in_order")
@inject
def delete_product_in_order(
        inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service]
) -> ResponseReturnValue:
    payload = DeleteInboundOrderProductSchema.model_validate(request.get_json() or {})
    dto = to_dto_delete_order_product(payload)
    read_dto = inbound_order_service.delete_product_in_order(dto)
    return jsonify({f"Product {read_dto} deleted successfully from inbound order {dto.inbound_order_id}"}), 200


# ----------------------------------------- Filters -----------------------------------------

@order_inbound_bp.get("/all")
@inject
def get_all_orders_with_products(
    inbound_order_service: InboundOrderService = Provide[Container.inbound_order_service]
):
    warehouse_id = request.args.get("warehouse_id", type=int)
    statuses = request.args.getlist("statuses") or None

    # konwersja stringów na enum
    converted_statuses = [InboundOrderStatus(s) for s in statuses] if statuses else None

    # pobranie DTO
    stock_action: list[ReadInboundOrderProductsWithOrderDTO] = inbound_order_service.get_all_orders_with_products(
        warehouse_id,
        converted_statuses
    )

    # mapowanie na schema
    response_data = [(to_schema_dto_inbound_order_with_products(dto).model_dump(mode='json')) for dto in stock_action]

    return jsonify(response_data)

# Do tego mozna ale nei trzeba wpisywac argumentow i tak URL'e beda wygladac:
"""
   GET /all
    GET /all?warehouse_id=5
    GET /all?status=approved&status=delivered
    GET /all?warehouse_id=5&status=approved&status=delivered
"""
