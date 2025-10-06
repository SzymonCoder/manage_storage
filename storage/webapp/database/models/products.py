from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from storage.webapp.extensions import db



#produkt ma miec id, sku, ean, nazwe produktu, data waznosci,
#data stworzenia produktu w bazie danych, cena zakupu netto, waluta


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    ean: Mapped[str] = mapped_column(String(14), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    expiration_date: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)


    created_at: Mapped[datetime] = mapped_column(DateTime(),nullable=False,server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    inventories: Mapped[list["Inventory"]] = relationship(
        back_populates="product"
    )
