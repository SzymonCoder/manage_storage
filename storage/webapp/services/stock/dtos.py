from sqlalchemy import create_engine, text, Engine
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class ExternalStockDTO(BaseModel):
    """
    Nasz wewnętrzny, standardowy format danych o stanie magazynowym
    pobranym z zewnętrznego systemu.
    """
    warehouse_id: int = Field(alias='warehouse_id')
    sku: str = Field(alias='sku')
    exp_date: datetime = Field(alias="exp_date")
    qty_per_date: int = Field(alias="qty_per_date")
    qty_total_sku: int = Field(alias="qty_total_sku")

    class Config:
        from_attributes = True  # Pozwala tworzyć DTO z obiektów (np. wierszy z SQLAlchemy)
        populate_by_name = True  # Umożliwia tworzenie obiektu używając aliasów LUB nazw pól

