# Plik: seed_data.py

from webapp.database.models.stocks_summary import StockSummary, StockQtyStatus
from webapp.extensions import db

# Prosty skrypt do dodania 5 wierszy do stocks_summary
def seed_stocks_summary():
    example_data = [
        StockSummary(
            warehouse_id=1,
            product_id=101,
            good_date_qty=50,
            medium_date_qty=20,
            critical_date_qty=10,
            expired_qty=5,
            qty_total_of_sku=85,
            ordered_in_qty=40,
            status_of_total_qty=StockQtyStatus.GOOD,
        ),
        StockSummary(
            warehouse_id=1,
            product_id=102,
            good_date_qty=30,
            medium_date_qty=10,
            critical_date_qty=5,
            expired_qty=1,
            qty_total_of_sku=46,
            ordered_in_qty=20,
            status_of_total_qty=StockQtyStatus.MEDIUM,
        ),
        StockSummary(
            warehouse_id=2,
            product_id=103,
            good_date_qty=70,
            medium_date_qty=30,
            critical_date_qty=0,
            expired_qty=0,
            qty_total_of_sku=100,
            ordered_in_qty=50,
            status_of_total_qty=StockQtyStatus.GOOD,
        ),
        StockSummary(
            warehouse_id=2,
            product_id=104,
            good_date_qty=40,
            medium_date_qty=20,
            critical_date_qty=10,
            expired_qty=0,
            qty_total_of_sku=70,
            ordered_in_qty=30,
            status_of_total_qty=StockQtyStatus.CRITICAL,
        ),
        StockSummary(
            warehouse_id=3,
            product_id=105,
            good_date_qty=10,
            medium_date_qty=5,
            critical_date_qty=5,
            expired_qty=0,
            qty_total_of_sku=20,
            ordered_in_qty=10,
            status_of_total_qty=StockQtyStatus.TOO_LOW,
        ),
    ]

    with db.session.begin():
        db.session.add_all(example_data)
        print("Dodano 5 wierszy do tabeli stocks_summary.")