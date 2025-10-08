from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Numeric, Text, Boolean, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ...extensions import db

from typing import TYPE_CHECKING

# Ten blok jest widoczny tylko dla edytora kodu, a nie dla Pythona podczas uruchamiania.
# Dzięki niemu edytor wie, czym jest 'ProductSupplierInfo'.
if TYPE_CHECKING:
    from .products_suppliers_info import ProductSupplierInfo
    from .inbound_orders import InboundOrder




class Product(db.Model):# type: ignore
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    ean: Mapped[str] = mapped_column(String(14), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_expiration_date: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_dose_product: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    days_of_dosage: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)


    created_at: Mapped[datetime] = mapped_column(DateTime(),nullable=False,server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (CheckConstraint('(is_dose_product = true and days_of_dosage > 0) or'
                                      '(is_dose_product = false and days_of_dosage is null)',
                                      name='chk_days_of_dosage_of_product'),
                      )

    inbound_orders: Mapped['InboundOrder'] = relationship(back_populates='product')

    products_suppliers_info: Mapped[list['ProductSupplierInfo']] = relationship(
        back_populates="product")

