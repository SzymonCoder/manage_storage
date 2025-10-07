from sqlalchemy import select
from ...extensions import db
from ..models.products_suppliers_info import ProductSupplierInfo
from .generic import GenericRepository
from decimal import Decimal


class ProductSupplierInfoRepository(GenericRepository[ProductSupplierInfo]):
    def __init__(self):
        super().__init__(ProductSupplierInfo)
    

# ------------------------ Aktualizacje statusow i opisu ------------------------

    def edit_price(self, product_supplier_info: ProductSupplierInfo, price: Decimal) -> None:
        product_supplier_info.net_price = price
        
    def edit_currency(self, product_supplier_info: ProductSupplierInfo, currency: str) -> None:
        product_supplier_info.currency = currency
        
    def edit_production_time_days(self, product_supplier_info: ProductSupplierInfo, days: int) -> None:
        product_supplier_info.production_time_days = days
        
    def edit_production_delivery_days(self, product_supplier_info: ProductSupplierInfo, days: int) -> None:
        product_supplier_info.production_delivery_days = days

# ------------------------ Aktualizacje statusow i opisu ------------------------

    def get_all_by_sku(self, sku: str ) -> list[ProductSupplierInfo] | None:
        stmt = select(ProductSupplierInfo).where(ProductSupplierInfo.id_product.is_(sku))
        return list(db.session.scalars(stmt))

    def get_all_by_supplier_id(self, supplier_id: int) -> list[ProductSupplierInfo] | None:
        stmt = select(ProductSupplierInfo).where(ProductSupplierInfo.id_supplier.is_(supplier_id))
        return list(db.session.scalars(stmt))

    def get_by_price_between(self, low_end: Decimal, high_end: Decimal) -> list[ProductSupplierInfo] | None:
        stmt = select(ProductSupplierInfo).where(ProductSupplierInfo.net_price.between(low_end, high_end))
        return list(db.session.scalars(stmt))