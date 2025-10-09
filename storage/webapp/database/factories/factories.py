from typing import Dict
from ..repositories.external_stock_repository import ExternalStockRepository
from ....webapp.settings import WarehouseExternalDBConfig


class ExternalStockRepositoryFactory:
    """
    Fabryka odpowiedzialna za tworzenie wyspecjalizowanych instancji
    ExternalStockRepository na podstawie konfiguracji.
    """

    def __init__(self, configs: Dict[str, WarehouseExternalDBConfig]):
        self._configs = configs
        print(f"Fabryka repozytoriów zainicjalizowana z {len(configs)} konfiguracjami.")

    def create_for_warehouse(self, warehouse_id: int) -> ExternalStockRepository:
        """
        Tworzy i zwraca repozytorium dla danego ID magazynu.
        """
        config_key = str(warehouse_id)
        if config_key not in self._configs:
            raise ValueError(f"Brak konfiguracji bazy danych dla magazynu o ID: {warehouse_id}")

        config = self._configs[config_key]

        return ExternalStockRepository(
            db_uri=config.uri,
            table_name=config.table_name,
            column_mappings=config.column_mappings
        )