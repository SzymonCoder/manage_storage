from flask import request, jsonify
from flask.typing import ResponseReturnValue
from dependency_injector.wiring import inject, Provide

from .mappers import to_schema_read_summary_stock, to_schema_stock_update_response, to_schema_dto_inb_qty_update
from ...database.models.stocks_summary import StockSummary
from ...database.models.stocks_with_exp_dates import StockWithExpDate
from webapp.api.stock_summary.schemas import StockResponseSchema, StockUpdateResponseSchema



from webapp.services.stock.service import StockService


from webapp.containers import Container
from . import stock_summary_bp



# ----------------------------------------- Update Stock -----------------------------------------
@stock_summary_bp.post("/update/<int:warehouse_id>")
@inject
def update_stocks(stock_service: StockService = Provide[Container.stock_service], warehouse_id: int = 1) -> ResponseReturnValue:
    stock_action = stock_service.update_stock_data(warehouse_id)
    return jsonify(to_schema_stock_update_response(stock_action).model_dump(mode='json')), 200


@stock_summary_bp.post("/update_stock_inbound_qty/<int:warehouse_id>")
@inject
def update_stocks_inbound_qty(stock_service: StockService = Provide[Container.stock_service], warehouse_id: int = 1) -> ResponseReturnValue:
    stock_action = stock_service.update_stock_summary_inbound_order_qty(warehouse_id)
    return jsonify(to_schema_dto_inb_qty_update(stock_action).model_dump(mode='json')), 200


# ----------------------------------------- Filters -----------------------------------------

@stock_summary_bp.get("/all")
@inject
def get_all_summary_stock(stock_service: StockService = Provide[Container.stock_service]) -> ResponseReturnValue:
    stock_action = stock_service.stocks_summary_repo.get_all()
    return jsonify([to_schema_read_summary_stock(dto).model_dump(mode='json') for dto in stock_action]), 200


@stock_summary_bp.get("/<int:warehouse_id>")
@inject
def get_summary_stock_by_wh_id(warehouse_id: int, stock_service: StockService = Provide[Container.stock_service]) -> ResponseReturnValue:
    stock_action = stock_service.stocks_summary_repo.get_by_warehouse_id(warehouse_id)
    return jsonify([to_schema_read_summary_stock(dto).model_dump(mode='json') for dto in stock_action]), 200




@stock_summary_bp.get("/<int:warehouse_id>/<string:sku>")
@inject
def get_summary_stock_by_wh_id_and_sku(
        warehouse_id: int,
        sku: str,
        stock_service: StockService = Provide[Container.stock_service]
        ) -> ResponseReturnValue:

    stock_dto = stock_service.stocks_summary_repo.get_by_warehouse_id_and_sku(warehouse_id, sku)
    response_stock = to_schema_read_summary_stock(stock_dto)
    return jsonify([schema.model_dump(mode='json') for schema in response_stock]), 200


@stock_summary_bp.get("<string:status_of_total_qty>/<int:warehouse_id>")
@inject
def get_summary_stock_by_status_of_total_qty(
        warehouse_id: int | None,
        status_of_total_qty: str,
        stock_service: StockService = Provide[Container.stock_service]
    ) -> ResponseReturnValue:
    status_of_total_qty = StockSummary.status_of_total_qty.get_enum_by_value(status_of_total_qty)
    stock_dto = stock_service.stocks_summary_repo.get_by_qty_status(status_of_total_qty, warehouse_id)
    response_stock = to_schema_read_summary_stock(stock_dto)
    return jsonify([schema.model_dump(mode='json') for schema in response_stock]), 200
