# plik z kontenerem dla repozytorium czy innych serwis tak by jeden kontenr byl odpalany w ramach jednej aplikacji
from dependency_injector import containers, providers
from database.repositories.inbound_orders import InboundOrderRepository
from database.repositories.products import ProductRepository
from database.repositories.products_suppliers_info import ProductSupplierInfoRepository
from database.repositories.stocks_summary import StockSummaryRepository
from database.repositories.stocks_with_exp_dates import StocksWithExpDateRepository
from database.repositories.suppliers import SupplierRepository
from database.repositories.warehouses import WarehouseRepository

from services.deliveries.services import DeliveryService
from services.stock.service import StockService


# Klasa Container to kontener DI, dziedziczacy po DeclarativeContainer i bedzie
# rejestrem dostawcow obiektow.
class Container(containers.DeclarativeContainer):

    # Ustawia domyslne miejsca, gdzie biblioteka bedzie wstrzykiwac zaleznosci.
    # Dzieki temu w tych miejscach uzyjesz @inject, Provide[...]
    wiring_config = containers.WiringConfiguration(
        packages=[
            "webapp.api" #zastanwoci sie czy nie podizelic Container na ContainerInboundOrder i Stock i zrobic dwa i podzielic w api na dwie paczki
        ]
    )

    # Definiujesz providerow, ktorzy beda dostarczac konkretne repo jako singletones.
    # Zawsze bedziemy korzystac z tej samej instancji konkretnego repo.
    inbound_order_repository = providers.Singleton(InboundOrderRepository)
    product_repository = providers.Singleton(ProductRepository)
    product_supplier_info_repository = providers.Singleton(ProductSupplierInfoRepository)
    stock_summary_repository = providers.Singleton(StockSummaryRepository)
    stocks_with_exp_dates_repository = providers.Singleton(StocksWithExpDateRepository)
    supplier_repository = providers.Singleton(SupplierRepository)
    warehouse_repository = providers.Singleton(WarehouseRepository)

    deliveries_service = providers.Singleton(
        DeliveryService,
        supplier_repository=supplier_repository,
        product_supplier_info_repository=product_supplier_info_repository,
        inbound_order_repository=inbound_order_repository,
        warehouse_repository=warehouse_repository,
    )


    stock_service = providers.Singleton(
        StockService,
        warehouse_repository=warehouse_repository,
        stock_summary_repository=stock_summary_repository,
        stocks_with_exp_dates_repository=stocks_with_exp_dates_repository,
        product_repository=product_repository,
    )