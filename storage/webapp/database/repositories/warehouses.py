from .suppliers import SupplierRepository
from ..models.warehouses import Warehouse


class WarehouseRepository(SupplierRepository):
    def __init__(self):
        super().__init__(model=Warehouse)



