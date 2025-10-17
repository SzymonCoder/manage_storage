from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, Boolean, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db

# Ten blok jest widoczny tylko dla edytora kodu, a nie dla Pythona podczas uruchamiania.
# Dzięki niemu edytor wie, czym jest 'ProductSupplierInfo'.
if TYPE_CHECKING:
    from .products_suppliers_info import ProductSupplierInfo
    from .inbound_orders import InboundOrder

class Supplier(db.Model):# type: ignore
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    nip_number: Mapped[str] = mapped_column(String(10), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    company_address: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(255), nullable=False)
    area_phone_number: Mapped[int] = mapped_column(Integer, nullable=False)
    phone_number: Mapped[int] = mapped_column(Integer, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    inbound_orders = relationship("InboundOrder", back_populates="supplier")


    products_suppliers_info: Mapped[list['ProductSupplierInfo']] = relationship(
        back_populates="suppliers"
    )



    __table_args__ = (CheckConstraint('area_phone_number > 0 and area_phone_number < 999',
                                      name='chk_area_phone_number_max_4_positiv_digits'),
                      )


