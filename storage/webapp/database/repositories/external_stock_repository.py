from sqlalchemy import create_engine, text, Engine
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict
from ....webapp.services.stock.dtos import ExternalStockDTO


class ExternalStockRepository:
    """
    Repozytorium odpowiedzialne za pobieranie danych z JEDNEJ, konkretnej,
    zewnętrznej bazy danych.

    Ta klasa nie jest już singletonem. Jest tworzona dynamicznie przez fabrykę
    dla każdego magazynu, z odpowiednią konfiguracją połączenia.
    """

    _engine: Engine
    _qualified_table_name: str
    _column_map: Dict[str, str]

    def __init__(self, db_uri: str, table_name: str, column_mappings: Dict[str, str]):

        # Tworzymy silnik SQLAlchemy dla podanego URI bazy danych.
        # pool_pre_ping=True zapewnia, że połączenie jest sprawdzane przed użyciem,
        # co zapobiega błędom po długim okresie nieaktywności.

        self._engine = create_engine(db_uri, pool_pre_ping=True, pool_recycle=3600)
        self._qualified_table_name = f"{table_name}"
        self._column_map = column_mappings
        print(f"Repozytorium skonfiguowane dla tabeli: '{self._qualified_table_name}'")


    def get_stock_data_from_warehouse(self, warehouse_id: int) -> List[ExternalStockDTO]:
        select_clause = ", ".join([
            f"{external_name} AS {internal_name}"
            for internal_name, external_name in self._column_map.items()
        ])

        # Pobranie zewnętrznej nazwy kolumny dla 'warehouse_ref' do użycia w WHERE
        wh_ref_column = self._column_map['warehouse_ref']

        with self._engine.connect() as connection:
            # Dynamiczne i bezpieczne budowanie zapytania
            query = text(f"""
                SELECT {select_clause}
                FROM {self._qualified_table_name}
                WHERE {wh_ref_column} = :wh_id
                ORDER BY {self._column_map['updated_at']} DESC;
            """)

            result = connection.execute(query, {"wh_id": warehouse_id})
            stock_data_rows = result.mappings().all()

        # Walidacja i transformacja wyników do listy naszych standardowych DTO
        # Pydantic automatycznie użyje aliasów zdefiniowanych w DTO!
        return [ExternalStockDTO.model_validate(dict(row)) for row in stock_data_rows]



