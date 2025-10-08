from sqlalchemy import select, update
from .generic import GenericRepository
from ..models.products import Product
from ...extensions import db



class ProductRepository(GenericRepository[Product]):
    def __init__(self):
        super().__init__(Product)


# ------------------------ Aktualizacje statusow i opisu ------------------------

    def set_exp_date_status(self, product: Product, status: bool) -> None:
        product.is_expiration_date = status

    """ Wykonuje PRAWDZIWĄ masową aktualizację statusu 'is_expiration_date' dla produktów.
    Generuje jedno zapytanie UPDATE w bazie danych.
    Zwraca liczbę zaktualizowanych wierszy.
    """

    def bulk_exp_date_status(self, skus: list[str], status: bool) -> None | int:
        stmt = (
            update(Product)
            .where(Product.id.in_(list(skus)))
            .values(is_expiration_date=status))

        result = db.session.execute(stmt)

        return result.rowcount



    def set_active_status(self, product: Product, status: bool) -> None:
        product.is_active = status


    def bulk_active_status(self, skus: list[str], status: bool) -> None | int:
        stmt = (
            update(Product)
            .where(Product.id.in_(list(skus)))
            .values(is_active=status))

        result = db.session.execute(stmt)

        return result.rowcount


    def set_dose_product_status(self, product: Product, status: bool, dosage: int | None) -> None:
        product.is_dose_product = status
        if status:
            if dosage is None or dosage <= 0:
                raise ValueError("Dosage must be greater than 0 if status is True")
            product.days_of_dosage = dosage
        else:
            # zwracany jest None bo w tabeli jest Null i trzeba to tak ustawic by nie bylo bledow
            product.days_of_dosage = None #type: ignore


    def update_description(self, product: Product, description: str) -> None:
        product.description = description


# ------------------------ Filtrowanie ------------------------

    def get_by_sku(self, sku: int) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        return db.session.scalar(stmt)

    def get_all_by_active_status(self, status: bool) -> list[Product] | None:
        stmt = select(Product).where(Product.is_active.is_(status))
        #alternatywa stmt = select(Product).where(Product.is_active == status)
        return list(db.session.scalars(stmt))

# TODO: dodać filtr po słowie kluczowym z opisu, oraz z nazwy