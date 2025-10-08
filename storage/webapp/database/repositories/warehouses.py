from sqlalchemy import select

from .suppliers import SupplierRepository
from ...extensions import db
from ..models.warehouses import Warehouse
from .generic import GenericRepository


class WarehouseRepository(SupplierRepository):
    def __init__(self):
        super().__init__(model=Warehouse)



