from datetime import datetime, timedelta
from itertools import groupby
from typing import cast

from sqlalchemy.orm import Mapped
from webapp.database.models.inbound_orders import InboundOrder
from webapp.database.models.products_suppliers_info import ProductSupplierInfo
from webapp.database.models.stocks_summary import StockSummary
from webapp.database.models.stocks_summary_arch import StockSummaryArch
from webapp.database.models.stocks_with_exp_dates import StockWithExpDate, ExpDateStatus, StockQtyStatus
from webapp.database.models.stocks_with_exp_dates_arch import StockWithExpDateArch
from webapp.database.repositories.external_stock_repository import ExternalStockRepository
from webapp.database.repositories.inbound_orders import InboundOrderRepository
from webapp.database.repositories.products_suppliers_info import ProductSupplierInfoRepository
from webapp.database.repositories.stock_summary_arch import StockSummaryArchRepository
from webapp.database.repositories.stock_with_exp_dates_arch import StockWithExpDateArchRepository
from webapp.database.repositories.stocks_summary import StockSummaryRepository
from webapp.database.repositories.stocks_with_exp_dates import StocksWithExpDateRepository
from webapp.extensions import db
from webapp.services.extension import (
    ServiceException,
    NotFoundDataException,
    ValidationException,

)

from .mapper import stock_to_dto, stock_summary_inbound_update_to_dto
from .mapper import to_dto_read_stock_with_exp_date, to_dto_read_stock_summary
from ...database.repositories.products import ProductRepository
from ...services.stock.dtos import ExternalStockDTO, StockSummaryInboundUpdateDTO, ReadStockExpDateDTO, StockSummaryDTO, \
    StockDTO


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
            product_repo: ProductRepository,
    ):

        self.inbound_orders_repo = inbound_orders_repo
        self.stocks_summary_repo = stocks_summary_repo
        self.stocks_with_exp_dates_repo = stocks_with_exp_dates_repo
        self.stock_summary_arch_repo = stock_summary_arch_repo
        self.stock_with_exp_dates_arch_repo = stock_with_exp_dates_arch_repo
        self.product_supplier_info_repo = product_supplier_info_repo
        self.external_stock_repo = external_stock_repo
        self.product_repo = product_repo

    def update_stock_data(self, warehouse_id: int = 1) -> StockDTO:
        external_stock = self.prepare_data_for_stock_update(warehouse_id)
        if not external_stock:
            raise ServiceException('Problem with import stock_summary and convert data')

        # ✅ USUŃ with db.session.begin():
        try:
            # Archiwizuj stare dane
            self.stocks_summary_repo.transfer_to_archive(warehouse_id)
            self.stocks_with_exp_dates_repo.transfer_to_archive(warehouse_id)

            # Dodaj nowe dane
            self.stocks_summary_repo.add_many(external_stock[0])
            self.stocks_with_exp_dates_repo.add_many(external_stock[1])

            # Commit wszystkich zmian naraz
            db.session.commit()

            # Aktualizuj ilości z zamówień
            self.update_stock_summary_inbound_order_qty(warehouse_id)

            return stock_to_dto(external_stock[0])

        except Exception as e:
            db.session.rollback()
            raise ServiceException(f'Failed to update stock data: {str(e)}')

    def update_stock_summary_inbound_order_qty(self, warehouse_id: int = 1) -> StockSummaryInboundUpdateDTO:

        all_stock_records = self.stocks_summary_repo.get_by_warehouse_id(warehouse_id)
        for record in all_stock_records:
            record.ordered_in_qty = 0

        ordered_qty_in = self.inbound_orders_repo.get_active_ordered_quantities(warehouse_id)

        updated_sku_count = 0
        updated_qty_count = 0

        for sku, value in ordered_qty_in.items():
            stock_record = self.stocks_summary_repo.get_by_warehouse_id_and_product_sku(warehouse_id, sku)

            if stock_record:
                stock_record.ordered_in_qty += value
                updated_sku_count += 1
                updated_qty_count += value

        # ✅ DODAJ commit
        db.session.commit()

        print(f'Stock summary updated with inbound orders')
        return stock_summary_inbound_update_to_dto(warehouse_id, updated_sku_count, updated_qty_count)

# ------------------------------------ Filtry StockWithExpDate ----------------------------------

    def get_all_stock(self) -> list[ReadStockExpDateDTO]:
        result = list(self.stocks_with_exp_dates_repo.get_all())

        if not result:
            raise NotFoundDataException('No stock data')

        return [to_dto_read_stock_with_exp_date(res) for res in result]



    def get_stock_by_warehouse_id(self, warehouse_id: int) -> list[ReadStockExpDateDTO] | None:
        result = self.stocks_with_exp_dates_repo.get_by_warehouse_id(warehouse_id)

        if not result:
            raise NotFoundDataException('No stock data')

        return [to_dto_read_stock_with_exp_date(res) for res in result]

    def get_stock_with_qty_status(self, status: str) -> list[ReadStockExpDateDTO]:
        result = self.stocks_with_exp_dates_repo.get_by_qty_status(status)
        if not result:
            raise NotFoundDataException('No stock data')

        return [to_dto_read_stock_with_exp_date(res) for res in result]


    def get_stock_with_exp_date_status(self, status: str) -> list[ReadStockExpDateDTO]:
        result = self.stocks_with_exp_dates_repo.get_by_exp_date_status(status)
        if not result:
            raise NotFoundDataException('No stock data')

        return [to_dto_read_stock_with_exp_date(res) for res in result]

    def get_stock_with_sku(self, sku: str) -> list[ReadStockExpDateDTO]:
        result = self.stocks_with_exp_dates_repo.get_by_sku(sku)
        if not result:
            raise NotFoundDataException('No stock data')

        return [to_dto_read_stock_with_exp_date(res) for res in result]


# ------------------------------------ Filtry StockSummary ----------------------------------


    def get_stock_with_warehouse_id_and_product_sku(self, warehouse_id: int, sku: str) -> StockSummaryDTO:
        result = self.stocks_summary_repo.get_by_warehouse_id_and_product_sku(warehouse_id, sku)
        if not result:
            raise NotFoundDataException('No stock data was found')

        return to_dto_read_stock_summary(result)


    def get_stock_by_qty_status(self, status: str, warehouse_id: int | None) -> list[StockSummaryDTO]:
        result = self.stocks_summary_repo.get_by_qty_status(status, warehouse_id)
        if not result:
            raise NotFoundDataException('No stock data was found')
        return [to_dto_read_stock_summary(res) for res in result]



# ------------------------------------ Funkcje do przygotowania aktualizacji stocku ----------------------------------
    def prepare_data_for_stock_update(self, warehouse_id: int = 1) -> tuple[list[StockSummary], list[StockWithExpDate]]:

        # pobranie danych z zewnarzt
        external_data_dtos = self.external_stock_repo.get_stock_data_from_warehouse(warehouse_id)

        if not external_data_dtos:
            raise NotFoundDataException('No data from external warehouses')

        # pogrupowanie danych po SKU
        dtos_by_sku = {k: list(v) for k, v in groupby(sorted(external_data_dtos, key=lambda d: d.sku), key=lambda d: d.sku)}
        # {
        #     "SKU123": [
        #         ExternalStockDTO(warehouse_id=1, sku="SKU123", exp_date="2025-10-15", qty_per_date=50,
        #                          qty_total_sku=300),
        #         ExternalStockDTO(warehouse_id=1, sku="SKU123", exp_date="2025-11-01", qty_per_date=30,
        #                          qty_total_sku=300)
        #     ],
        #     "SKU456": [
        #         ExternalStockDTO(warehouse_id=1, sku="SKU456", exp_date="2025-10-20", qty_per_date=20,
        #                          qty_total_sku=150),
        #         ExternalStockDTO(warehouse_id=1, sku="SKU456", exp_date="2025-11-20", qty_per_date=40,
        #                          qty_total_sku=150)
        #     ],
        #     "SKU789": [
        #         ExternalStockDTO(warehouse_id=1, sku="SKU789", exp_date="2025-12-10", qty_per_date=10,
        #                          qty_total_sku=100)
        #     ]
        # }


        product_map = self.product_repo.get_dict_of_all_sku()

        stock_summary = []
        stock_with_exp_date = []

        for sku, product_dtos in dtos_by_sku.items():
            product_id = product_map.get(sku)
            if not product_id:
                raise NotFoundDataException(f'Product {sku} not found')
            # Delegowanie tworzenia podsumowania i szczegółów
            summary = self.create_stock_summary(product_dtos, warehouse_id, sku, product_id)
            details = self.create_stock_with_exp_date(product_dtos, warehouse_id, product_id)

            stock_summary.append(summary)
            stock_with_exp_date.extend(details)

        #
        # if stock_summary:
        #     first_summary = stock_summary[0]
        #     if not hasattr(first_summary, 'good_date_qty'):
        #         raise ServiceException('prepare_data_for_stock_update produced unexpected first list (expected StockSummary items)')
        #
        # if stock_with_exp_date:
        #     first_detail = stock_with_exp_date[0]
        #     if not hasattr(first_detail, 'qty_per_exp_date'):
        #         raise ServiceException('prepare_data_for_stock_update produced unexpected second list (expected StockWithExpDate items)')


        return stock_summary, stock_with_exp_date






    def create_stock_summary(self, dtos_of_sku: list[ExternalStockDTO], warehouse_id: int, sku: str, product_id: int) -> StockSummary:

        summary = StockSummary(
            warehouse_id=warehouse_id,
            product_id=product_id,
            good_date_qty=0,
            medium_date_qty=0,
            critical_date_qty=0,
            expired_qty=0,
            qty_total_of_sku=dtos_of_sku[0].qty_total_of_sku,
            status_of_total_qty=self._check_stock_qty_status(dtos_of_sku[0]),
            ordered_in_qty=self.inbound_orders_repo.get_qty_of_ordered_in_product(warehouse_id, sku)
        )

        for dto in dtos_of_sku:
            status = self._check_exp_date_status(dto)
            if status == ExpDateStatus.GOOD:
                summary.good_date_qty += dto.qty_per_exp_date
            elif status == ExpDateStatus.MEDIUM:
                summary.medium_date_qty += dto.qty_per_exp_date
            elif status == ExpDateStatus.CRITICAL:
                summary.critical_date_qty += dto.qty_per_exp_date
            else:  # EXPIRED
                summary.expired_qty += dto.qty_per_exp_date

        return summary




    def create_stock_with_exp_date(self, dtos_of_sku: list[ExternalStockDTO], warehouse_id: int, product_id: int) -> list[StockWithExpDate]:
        details_list = []
        for dto in dtos_of_sku:
            detail = StockWithExpDate(
                warehouse_id = warehouse_id,  # Łączymy szczegół z jego podsumowaniem
                product_id = product_id,
                expiration_date=dto.expiration_date,
                qty_per_exp_date=dto.qty_per_exp_date,
                qty_total_of_sku=dto.qty_total_of_sku,
                status_of_exp_date=self._check_exp_date_status(dto),
                status_of_total_qty=self._check_stock_qty_status(dto)
            )
            details_list.append(detail)
        return details_list




    def _check_exp_date_status(self, dto: ExternalStockDTO) -> ExpDateStatus:

        is_dosage_product = self.product_repo.get_by_sku(dto.sku)

        if is_dosage_product.is_expiration_date is False:
            return ExpDateStatus.NOT_APPLY

        exp_date = dto.expiration_date
        dosage_days = self._get_dosage_day(dto.sku) or 0
        today = datetime.now().date()

        if exp_date < today + timedelta(days=7) + timedelta(days=dosage_days):
            return ExpDateStatus.EXPIRED
        if exp_date < today + timedelta(days=30) + timedelta(days=dosage_days):
            return ExpDateStatus.CRITICAL
        if exp_date < today + timedelta(days=90) + timedelta(days=dosage_days):
            return ExpDateStatus.MEDIUM
        return ExpDateStatus.GOOD


    def _check_stock_qty_status(self, dto: ExternalStockDTO) -> StockQtyStatus:
        avg_order_qty = 1 # TODO: ogarnąć jak albo lepiej skad pobierac dane na temat wysylki outbound, moze z zewnatrz?

        prod_sup_info = self.product_supplier_info_repo.get_all_by_sku(dto.sku)

        if not prod_sup_info:
            raise ValueError(f'Product {dto.sku} has no supplier info')

        lowest_supplier_production = 999
        for sup in prod_sup_info:
            total_days = sup.production_time_days + sup.production_delivery_days
            if total_days < lowest_supplier_production:
                lowest_supplier_production = total_days

        days_left = dto.qty_total_of_sku // avg_order_qty
        if dto.qty_total_of_sku == 0:
            return StockQtyStatus.EMPTY.value
        if days_left > lowest_supplier_production + 120:
            return StockQtyStatus.GOOD.value
        elif days_left > lowest_supplier_production + 30:
            return StockQtyStatus.MEDIUM.value
        elif days_left > lowest_supplier_production + 10:
            return StockQtyStatus.CRITICAL.value
        else:
            return StockQtyStatus.TOO_LOW.value




    def _get_dosage_day(self, sku: str) -> Mapped[int]:

        # prod_sup_info = self.product_supplier_info_repo.get_all_by_sku(sku)
        # if not prod_sup_info:
        #     raise ValueError(f'Product {sku} has no supplier info')
        #
        # product = prod_sup_info[0]
        product = self.product_repo.get_by_sku(sku)


        return product.days_of_dosage
