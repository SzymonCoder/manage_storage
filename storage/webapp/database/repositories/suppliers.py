from sqlalchemy import select
from typing import Type
from ...extensions import db
from ..models.suppliers import Supplier
from .generic import GenericRepository
from flask_sqlalchemy.model import Model



class SupplierRepository(GenericRepository[Supplier]):
    def __init__(self, model: Type[Model] | None = None):
        super().__init__(Supplier)


# ------------------------ Aktualizacje statusow i opisu ------------------------

    def edit_name(self, supplier: Supplier, name: str) -> None:
        supplier.name = name

    def edit_nip(self, supplier: Supplier, nip_number: str) -> None:
        supplier.nip = nip_number

    def edit_country(self, supplier: Supplier, country: str) -> None:
        supplier.country = country

    def edit_company_address(self, supplier: Supplier, company_address: str) -> None:
        supplier.company_address = company_address

    def edit_contact_person(self, supplier: Supplier, contact_person: str) -> None:
        supplier.contact_person = contact_person

    def edit_area_phone_number(self, supplier: Supplier, area_phone_number: int) -> None:
        if 999 < area_phone_number < 0:
            raise ValueError('Phone number cannot be negative or higher than 999')
        area_phone_number = area_phone_number

    def edit_email(self, supplier: Supplier, email: str) -> None:
        supplier.email = email

    def set_active_status(self, supplier: Supplier, status: bool) -> None:
        supplier.is_active = status

# ------------------------ Filtry ------------------------

    def get_all_by_active_status(self, status: bool) -> list[Supplier] | None:
        stmt = select(Supplier).where(Supplier.is_active.is_(status))
        #alternatywa stmt = select(Product).where(Product.is_active == status)
        return list(db.session.scalars(stmt))

    def get_by_id(self, id: int) -> Supplier | None:
        stmt = select(Supplier).where(Supplier.id == id)
        return db.session.scalar(stmt)


    # TODO ogarnąć po nazwach np. albo po kraju :)


