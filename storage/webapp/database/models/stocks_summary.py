from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ...extensions import db


class StockSummary(db.Model):
    __tablename__ = "stocks_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    #columny i ilosci w danym statusie daty
    good_date_qty: Mapped[int] = mapped_column(Integer, nullable=True)
    medium_date_qty: Mapped[int] = mapped_column(Integer, nullable=True)
    critical_date_qty: Mapped[int] = mapped_column(Integer, nullable=True)
    expired_qty: Mapped[int] = mapped_column(Integer, nullable=True)

    qty_total_of_sku: Mapped[int] = mapped_column(Integer, nullable=True)
    status_of_total_qty: Mapped[Enum] = mapped_column(Enum('good_qty', 'medium_qty', 'critical_qty', 'no_products'))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )