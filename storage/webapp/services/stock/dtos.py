from sqlalchemy import create_engine, text, Engine
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Mapping
from dataclasses import dataclass


# class ExternalStockDTO(BaseModel):
#     """
#     Nasz wewnętrzny, standardowy format danych o stanie magazynowym
#     pobranym z zewnętrznego systemu.
#     """
#     warehouse_id: int = Field(alias='warehouse_id')
#     sku: str = Field(alias='sku')
#     exp_date: datetime = Field(alias="exp_date")
#     qty_per_date: int = Field(alias="qty_per_date")
#     qty_total_sku: int = Field(alias="qty_total_sku")
#
#     class Config:
#         from_attributes = True  # Pozwala tworzyć DTO z obiektów (np. wierszy z SQLAlchemy)
#         populate_by_name = True  # Umożliwia tworzenie obiektu używając aliasów LUB nazw pól



@dataclass(frozen=True)
class UpdateStockDTO:
    warehouse_id: int

@dataclass(frozen=True)
class ExternalStockDTO:
    sku: str = Field(alias='product_code')
    expiration_date: datetime = Field(alias='exp_date')
    qty_per_exp_date: int = Field(alias='qty_exp_date')
    qty_total_of_sku: int = Field(alias='qty_total_sku')

    @classmethod
    def model_validate(cls, row: Mapping[str, Any]):
        return cls(
            sku=str(row["product_code"]),
            expiration_date=datetime.fromisoformat(row["exp_date"]),
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
