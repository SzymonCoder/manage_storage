from __future__ import annotations

import os
import json
from typing import Dict, List, Any, TypedDict, cast
from sqlalchemy import create_engine, text, Engine
from dotenv import load_dotenv
from flask import current_app
from webapp.settings import Config

# Upewnij się, że ten import jest poprawny w Twojej strukturze projektu
from webapp.services.stock.dtos import ExternalStockDTO


load_dotenv()


class _WarehouseCacheEntry(TypedDict):
    """Definiuje strukturę wpisu w cache dla konfiguracji magazynu."""
    engine: Engine
    table_name: str
    column_map: Dict[str, str]


class ExternalStockRepository:
    """
    Repozytorium odpowiedzialne za pobieranie danych z zewnętrznych baz danych
    per-magazyn. Ładuje konfigurację z app.config['WAREHOUSE_DB_CONFIGS'] i
    leniwie tworzy silniki SQLAlchemy dla każdego magazynu.
    """

    _configs: Dict[str, Any]
    _engines_cache: Dict[str, Engine]
    _cache: Dict[str, _WarehouseCacheEntry]

    def __init__(self) -> None:
        configs_json = os.getenv("WAREHOUSE_DB_CONFIGS")
        if not configs_json:
            raise RuntimeError(
                "Brak zmiennej środowiskowej WAREHOUSE_DB_CONFIGS z konfiguracją baz danych."
            )

        try:
            self._configs = json.loads(configs_json)
        except json.JSONDecodeError:
            raise RuntimeError("WAREHOUSE_DB_CONFIGS nie jest poprawnym JSON-em.")

        self._engines_cache = {}
        self._cache = {}

    # ------------------------------------ Helpers ------------------------------------
    def _get_warehouse_config(self, warehouse_id: int) -> Dict[str, Any]:
        """Pobiera konfigurację i silnik bazy danych dla danego magazynu, używając cache."""
        wid = str(warehouse_id)

        if wid in self._engines_cache:
            config = self._configs[wid]
            config['engine'] = self._engines_cache[wid]
            return config

        if wid not in self._configs:
            raise RuntimeError(
                f"Brak konfiguracji dla magazynu o ID={warehouse_id} w WAREHOUSE_DB_CONFIGS."
            )

        config = self._configs[wid]
        db_uri = config.get('uri')
        table_name = config.get('table_name')
        column_mappings = config.get('column_mappings')

        if not all([db_uri, table_name, column_mappings]):
            raise RuntimeError(
                f"Niekompletna konfiguracja dla magazynu o ID={warehouse_id}. "
                "Wymagane klucze: 'uri', 'table_name', 'column_mappings'."
            )

        engine = create_engine(db_uri, pool_pre_ping=True, pool_recycle=1800)
        self._engines_cache[wid] = engine
        config['engine'] = engine

        return config


    def _get_configs(self) -> Dict[str, Any]:
        # Ta metoda może wymagać dopracowania w zależności od logiki, ale typy są poprawne
        if hasattr(self, '_configs') and self._configs is not None:
            return self._configs
        try:
            # Prefer Flask app config when in app context
            return current_app.config.get('WAREHOUSE_DB_CONFIGS', {})
        except RuntimeError:
            # Fallback for calls made outside application context (e.g., tests)

            return Config.WAREHOUSE_DB_CONFIGS

    def _ensure_warehouse(self, warehouse_id: int) -> _WarehouseCacheEntry:
        wid = str(warehouse_id)
        if wid in self._cache:
            return self._cache[wid]

        configs = self._get_configs()
        if not configs or wid not in configs:
            raise RuntimeError(
                f"External DB config not found for warehouse_id={warehouse_id}. "
                f"Ensure WAREHOUSE_DB_CONFIGS is set in environment/app config."
            )

        cfg = configs[wid]
        db_uri = getattr(cfg, 'uri', cfg.get('uri'))
        table_name = getattr(cfg, 'table_name', cfg.get('table_name'))
        column_mappings = getattr(cfg, 'column_mappings', cfg.get('column_mappings'))

        if not db_uri or not table_name or not column_mappings:
            raise RuntimeError(
                f"Incomplete external DB config for warehouse_id={warehouse_id}. Got: {cfg}"
            )

        engine = create_engine(db_uri, pool_pre_ping=True, pool_recycle=1800)
        self._cache[wid] = cast(_WarehouseCacheEntry, cast(object, {
            "engine": engine,
            "table_name": table_name,
            "column_map": column_mappings,
        }))
        return self._cache[wid]

    # ------------------------------------ Public API ------------------------------------
    def get_stock_data_from_warehouse(self, warehouse_id: int) -> List[ExternalStockDTO]:
        """Pobiera i przekształca dane o stanie magazynowym dla określonego magazynu."""

        config = self._get_warehouse_config(warehouse_id)
        column_map = config["column_mappings"]

        required_keys = ("product_code", "exp_date", "qty_exp_date", "qty_total_sku", "warehouse_ref", "updated_at")
        for key in required_keys:
            if key not in column_map:
                raise RuntimeError(
                    f"Brak wymaganego klucza '{key}' w 'column_mappings' dla magazynu ID={warehouse_id}."
                )

        select_clause = ", ".join(
            [f'"{external}" AS "{internal}"' for internal, external in column_map.items()]
        )
        wh_ref_column = column_map["warehouse_ref"]
        table = config["table_name"]
        engine: Engine = config["engine"]

        with engine.connect() as connection:
            query = text(
                f'SELECT {select_clause} FROM "{table}" '
                f'WHERE "{wh_ref_column}" = :wh_id '
                f'ORDER BY "{column_map["updated_at"]}" DESC'
            )
            result = connection.execute(query, {"wh_id": warehouse_id})
            rows = result.mappings().all()

        return [ExternalStockDTO.model_validate(dict(row)) for row in rows]