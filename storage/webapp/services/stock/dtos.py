from pydantic import Field
from datetime import datetime, date
from typing import Mapping, Any, Literal
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateStockDTO:
    warehouse_id: int

@dataclass(frozen=True)
class ExternalStockDTO:
    sku: str = Field(alias='product_code')
    expiration_date: date = Field(alias='exp_date')
    qty_per_exp_date: int = Field(alias='qty_exp_date')
    qty_total_of_sku: int = Field(alias='qty_total_sku')

    @classmethod
    def model_validate(cls, row: Mapping[str, Any]):
        exp_value = row.get("exp_date")
        # zostawiamy datę lub datetime tak, jak jest
        # nie robimy datetime.fromisoformat ani str
        return cls(
            sku=str(row["product_code"]),
            expiration_date=exp_value,
            qty_per_exp_date=int(row["qty_exp_date"]),
            qty_total_of_sku=int(row["qty_total_sku"])
        )


@dataclass(frozen=True)
class StockDTO:
    warehouse_id: int
    qty_total_of_sku: int
    qty_added_products : int



@dataclass(frozen=True)
class StockSummaryInboundUpdateDTO:
    warehouse_id: int
    updated_sku_qty: int
    updated_qty: int


@dataclass(frozen=True)
class StockSummaryDTO:
    warehouse_id: int
    product_id: int
    good_date_qty: int
    medium_date_qty: int
    critical_date_qty: int
    expired_qty: int
    qty_total_of_sku: int
    ordered_in_qty: int
    status_of_total_qty: str
    created_at: datetime

# ---------------------------------------- Stock Exp Date DTOs ----------------------------------------

@dataclass(frozen=True)
class ReadStockExpDateDTO:
    warehouse_id: int
    product_id: int
    expiration_date: datetime
    qty_per_exp_date: int
    qty_total_of_sku: int
    status_of_exp_date: str
    status_of_total_qty: str