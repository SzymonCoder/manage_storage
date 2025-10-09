from ....webapp.database.models.inbound_orders import InboundOrder
from ....webapp.database.models.stocks_summary import StockSummary
from ....webapp.database.models.stocks_with_exp_dates import StockWithExpDate
from ....webapp.database.models.stocks_summary_arch import StockSummaryArch
from ....webapp.database.models.stocks_with_exp_dates_arch import  StockWithExpDateArch
from ....webapp.database.models.products_suppliers_info import ProductSupplierInfo


from ....webapp.database.repositories.inbound_orders import InboundOrderRepository
from ....webapp.database.repositories.stocks_summary import StockSummaryRepository
from ....webapp.database.repositories.stocks_with_exp_dates import StocksWithExpDateRepository
from ....webapp.database.repositories.stock_summary_arch import StockSummaryArchRepository
from ....webapp.database.repositories.stock_with_exp_dates_arch import StockWithExpDateArchRepository
from ....webapp.database.repositories.products_suppliers_info import ProductSupplierInfoRepository
from ....webapp.database.repositories.external_stock_repository import ExternalStockRepository


from ....webapp.extensions import db

from ....webapp.services.extension import (
    ServiceException,
    NotFoundDataException,
    ValidationException,

)

from ...services.stock.dtos import ExternalStockDTO

from ....webapp.services.stock.mappers import StockMapper

# POBRAC TRZEBA DTO's ORAZ MAPEPRY W ZALEZNOSCI CO CHCEMY ROBIC W SERWIS WIEC TRZEBA TAKEI DTOS STWORZYC I MAPEPRY


class StockService:
    def __init__(
            self,
            inbound_orders_repo: InboundOrderRepository,
            stocks_summary_repo: StockSummaryRepository,
            stocks_with_exp_dates_repo: StocksWithExpDateRepository,
            stock_summary_arch_repo: StockSummaryArchRepository,
            stock_with_exp_dates_arch_repo: StockWithExpDateArchRepository,
            product_supplier_info_repo: ProductSupplierInfoRepository,
            external_stock_repo: ExternalStockRepository,
            stock_mapper: StockMapper
    ):

        self.inbound_orders_repo = inbound_orders_repo
        self.stocks_summary_repo = stocks_summary_repo
        self.stocks_with_exp_dates_repo = stocks_with_exp_dates_repo
        self.stock_summary_arch_repo = stock_summary_arch_repo
        self.stock_with_exp_dates_arch_repo = stock_with_exp_dates_arch_repo
        self.product_supplier_info_repo = product_supplier_info_repo
        self.external_stock_repo = external_stock_repo
        self.stock_mapper = stock_mapper



    def update_stock_data(self, warehouse_id: int = 1):

        dtos = self.external_stock_repo.get_stock_data_from_warehouse(warehouse_id)

        try:
            summaries, exp_date = self.stock_mapper.prepare_models_from_external_data(warehouse_id, dtos)
            self.stocks_summary_repo.transfer_to_archive(warehouse_id)
            self.stocks_with_exp_dates_repo.transfer_to_archive(warehouse_id)

            self.stocks_summary_repo.add_many(summaries)
            self.stocks_with_exp_dates_repo.add_many(exp_date)
        except Exception as e:
            db.session.rollback()

            raise ServiceException('Nie udalo sie zaktualizowac bazy danych')

        finally:
            db.session.commit()















        """"
        1. pobranie i sprawdzenie poalczenia - > jedna funckcja
        2. jesli pobieranie okej to wtedy obliczenia odpowiednie tak by dopasowac to 
         beda dwie funkcje poniewaz sa one p[otrzebne do dwoc tabel
        3. potrzebne z repo do transferu, jesli blad to rtollback"""

    def import_external_stock(self, warehouse_id: int = 1) -> list[ExternalStockDTO] | None:
        return self.external_stock_repo.get_stock_data_from_warehouse(warehouse_id)



# co ma robic:
"""
1. pobieranie danych cyklicznie
2. dane pobrane zwalidowac ?
3. Przeksztalcic dane do odpowiednich modeli za pomoca mappers
4. Zapisywanie do bazy danych

"""