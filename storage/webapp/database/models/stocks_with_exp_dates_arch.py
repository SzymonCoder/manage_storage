from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Integer, String, DateTime, Boolean, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .stocks_with_exp_dates import ExpDateStatus, StockQtyStatus
from ...extensions import db

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .warehouses import Warehouse




class StockWithExpDateArch(db.Model): # type: ignore
    __tablename__ = "stocks_with_exp_dates_arch"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    expiration_date: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    qty_per_exp_date: Mapped[int] = mapped_column(Integer, nullable=True)
    qty_total_of_sku: Mapped[int] = mapped_column(Integer, nullable=True)


    status_of_exp_date: Mapped[ExpDateStatus] = mapped_column(
        Enum(ExpDateStatus,
        name='exp_date_status')
    )

    status_of_total_qty: Mapped[StockQtyStatus] = mapped_column(
        Enum(StockQtyStatus,
        name='stock_qty_status')
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    warehouse: Mapped['Warehouse'] = relationship(
        back_populates='stocks_with_exp_dates_arch'
    )