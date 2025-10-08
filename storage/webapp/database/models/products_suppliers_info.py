from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Integer, func, Numeric, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from ...extensions import db
from typing import TYPE_CHECKING

# Ten blok jest widoczny tylko dla edytora kodu, a nie dla Pythona podczas uruchamiania.
# Dzięki niemu edytor wie, czym jest 'ProductSupplierInfo'.
if TYPE_CHECKING:
    from .products import Product
    from .suppliers import Supplier


#jest to sprawdzenie statyczny przez mypy wiec db.Model laczy sie w Alchemy i mypy tego nie ogarnia
class ProductSupplierInfo(db.Model): # type: ignore
    __tablename__ = "products_suppliers_info"

    id_product: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    id_supplier: Mapped[int] = mapped_column(ForeignKey('suppliers.id'), primary_key=True)
    net_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

# TODO dodać currency jako pozycje z tabeli nowej, Currency, ktora pobiera aktualny stan currency wobec PLN

    production_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    production_delivery_days: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


    product: Mapped["Product"] = relationship(back_populates="products_suppliers_info")
    supplier: Mapped["Supplier"] = relationship(back_populates="products_suppliers_info")

    __table_args__ = (CheckConstraint('production_time_days > 0',
                                      name='chk_production_time_days_positiv_digits'),
                      CheckConstraint('production_delivery_days > 0',
                                      name='chk_production_delivery_days_positiv_digits'),
                      )