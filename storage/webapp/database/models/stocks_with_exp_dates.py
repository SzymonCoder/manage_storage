from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ...extensions import db


class StockWithExpDate(db.Model):
    __tablename__ = "stocks_with_exp_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    expiration_date: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    qty_per_exp_date: Mapped[int] = mapped_column(Integer, nullable=True)
    qty_total_of_sku: Mapped[int] = mapped_column(Integer, nullable=True)

    # takie powinny być statusy w exp_date_status:
    # ('good_date', 'medium_date', 'critical_date', 'expired', 'no_products', 'N/D')
    status_of_exp_date: Mapped[str] = mapped_column(String(50),nullable=False)

    status_of_total_qty: Mapped[Enum] = mapped_column(Enum('good_qty', 'medium_qty', 'critical_qty', 'no_products'))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )