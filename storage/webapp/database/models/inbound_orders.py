from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ...extensions import db

from enum import Enum as PyEnum

class InboundOrderStatus(PyEnum):
    CREATED = 'created'
    APPROVED = 'approved'
    PRODUCED = 'produced'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class InboundOrder(db.Model):
    __tablename__ = "inbound_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey('suppliers.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[InboundOrderStatus] = mapped_column(Enum(InboundOrderStatus, name='inbound_order_status'))
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