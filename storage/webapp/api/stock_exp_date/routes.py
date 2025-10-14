from flask import request, jsonify
from flask.typing import ResponseReturnValue
from dependency_injector.wiring import inject, Provide

from ....webapp.services.stock.service import StockWithExpDate

from ....webapp.containers import Container
from . import stock_exp_date_bp


from .mappers import to_schema_read_stock_with_exp_date


# ----------------------------------------- Filters -----------------------------------------
@stock_exp_date_bp.get("/all")
@inject
def get_all_stock_with_exp_date(
        stock_service: StockWithExpDate = Provide[Container.stock_service],
        warehouse_id: int = 1
    ) -> ResponseReturnValue:

    stock_action = stock_service.get_all_stock()
    return jsonify([to_schema_read_stock_with_exp_date(stock).model_dump(mode='json') for stock in stock_action]), 200


@stock_exp_date_bp.get("/<int:warehouse_id>")
@inject
def get_all_stock_with_exp_date_by_warehouse_id(
        warehouse_id: int,
        stock_service: StockWithExpDate = Provide[Container.stock_service]
    ) -> ResponseReturnValue:
    stock_action = stock_service.get_all_by_warehouse_id(warehouse_id)
    return jsonify([to_schema_read_stock_with_exp_date(stock).model_dump(mode='json') for stock in stock_action]), 200