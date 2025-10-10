from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, func, ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ...extensions import db
from enum import Enum as PyEnum
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .products import Product
    from .suppliers import Supplier

class InboundOrderStatus(PyEnum):
    CREATED = 'created'
    APPROVED = 'approved'
    PRODUCED = 'produced'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class InboundOrder(db.Model): # type: ignore
    __tablename__ = "inbound_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey('suppliers.id'), nullable=False)
    status: Mapped[InboundOrderStatus] = mapped_column(
        Enum(InboundOrderStatus, name='inbound_order_status'),
        default=InboundOrderStatus.CREATED)
    # user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False) #przy tworzeniu zamówienia, trzeba
    # zrobić takie cos: from flask_login import current_user
    # InboundOrder(user_id=current_user.id)

    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # user: Mapped["User"] = relationship("User", back_populates="orders")


    supplier: Mapped["Supplier"] = relationship(back_populates='inbound_orders')
    product: Mapped["Product"] = relationship(back_populates='inbound_orders')




class InbounOrderProduct(db.Model):
    __tablename__ = "inbound_order_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inbound_order_id: Mapped[int] = mapped_column(ForeignKey('inbound_orders.id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    net_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True)


    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )