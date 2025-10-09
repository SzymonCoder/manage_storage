from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from itertools import groupby

from .dtos import ExternalStockDTO
from ...database.models.stocks_with_exp_dates import ExpDateStatus
from ....webapp.database.models.stocks_summary import StockSummary
from ....webapp.database.models.stocks_with_exp_dates import StockWithExpDate, StockQtyStatus
from ....webapp.database.repositories.products import ProductRepository


# Wersja uproszczona, bez wstrzykiwania repozytoriów dla jasności przykładu
class StockMapper:
    """
    Transformuje listę ExternalStockDTO na gotowe do zapisu modele bazodanowe.
    """
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo


    # 1. GŁÓWNA METODA PUBLICZNA - ORKIESTRATOR
    def prepare_models_from_external_data(
            self,
            warehouse_id: int,
            dtos: List[ExternalStockDTO]
    ) -> Tuple[List[StockSummary], List[StockWithExpDate]]:
        """
        Orkiestruje proces transformacji.
        Jej JEDYNĄ odpowiedzialnością jest GRUPOWANIE i DELEGOWANIE.
        """
        # Grupujemy wszystkie DTO po kluczu (SKU), aby przetwarzać każdy produkt osobno
        dtos_by_sku = {k: list(v) for k, v in groupby(sorted(dtos, key=lambda d: d.sku), key=lambda d: d.sku)}


        product_map = self.product_repo.get_dict_of_all_sku() # Mapa {sku: product_id}


        all_summaries = []
        all_details = []

        for sku, product_dtos in dtos_by_sku.items():
            product_id = product_map.get(sku)
            if not product_id:
                # Logowanie lub obsługa SKU, którego nie ma w naszej bazie
                continue

            # Delegowanie tworzenia podsumowania i szczegółów
            summary = self._prepare_summary_for_product(warehouse_id, product_id, product_dtos)
            details = self._prepare_details_for_product(summary, product_dtos)

            all_summaries.append(summary)
            all_details.extend(details)

        return all_summaries, all_details

    # 2. PRYWATNA METODA POMOCNICZA - JEDNA ODPOWIEDZIALNOŚĆ
    def _prepare_summary_for_product(
            self,
            warehouse_id: int,
            product_id: int,
            dtos_for_product: List[ExternalStockDTO]
    ) -> StockSummary:
        """
        Jej JEDYNĄ odpowiedzialnością jest AGREGACJA i stworzenie JEDNEGO StockSummary.
        """
        summary = StockSummary(
            warehouse_id=warehouse_id,
            product_id=product_id,
            good_date_qty=0,
            medium_date_qty=0,
            critical_date_qty=0,
            expired_qty=0,
            qty_total_of_sku=0
        )

        for dto in dtos_for_product:
            status = self._get_status_for_date(dto.exp_date)
            if status == StockQtyStatus.GOOD:
                summary.good_date_qty += dto.qty_per_date
            elif status == StockQtyStatus.MEDIUM:
                summary.medium_date_qty += dto.qty_per_date
            elif status == StockQtyStatus.CRITICAL:
                summary.critical_date_qty += dto.qty_per_date
            else:  # EXPIRED
                summary.expired_qty += dto.qty_per_date

            summary.qty_total_of_sku += dto.qty_per_date

        # Tutaj logika dla statusu ogólnego, np.
        # summary.status_of_total_qty = ...

        return summary

    # 3. PRYWATNA METODA POMOCNICZA - JEDNA ODPOWIEDZIALNOŚĆ
    def _prepare_details_for_product(
            self,
            summary: StockSummary,
            dtos_for_product: List[ExternalStockDTO]
    ) -> List[StockWithExpDate]:
        """
        Jej JEDYNĄ odpowiedzialnością jest mapowanie 1-do-1 z DTO na StockWithExpDate.
        """
        details_list = []
        for dto in dtos_for_product:
            detail = StockWithExpDate(
                stock_summary=summary,  # Łączymy szczegół z jego podsumowaniem
                exp_date=dto.exp_date,
                quantity=dto.qty_per_date,
                status=self._get_status_for_date(dto.exp_date, dto.dosage_day),
            )
            details_list.append(detail)
        return details_list

    # 4. PRYWATNA METODA POMOCNICZA - JEDNA ODPOWIEDZIALNOŚĆ
    def _get_status_for_date(self, exp_date: datetime, dosage_day: int) -> ExpDateStatus:
        """Jej JEDYNĄ odpowiedzialnością jest klasyfikacja daty ważności."""
        today = datetime.now()
        if exp_date < today + timedelta(days=7) + timedelta(days=dosage_day):
            return ExpDateStatus.EXPIRED
        if exp_date < today + timedelta(days=30) + timedelta(days=dosage_day):
            return ExpDateStatus.CRITICAL
        if exp_date < today + timedelta(days=90) + timedelta(days=dosage_day):
            return ExpDateStatus.MEDIUM
        return ExpDateStatus.GOOD