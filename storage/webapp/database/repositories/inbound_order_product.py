from sqlalchemy import select

from .generic import GenericRepository
from ..models.inbound_orders import InboundOrderProduct
from ..models.products import Product
from ...extensions import db


class InboundOrderProductRepository(GenericRepository[InboundOrderProduct]):
    def __init__(self):
        super().__init__(InboundOrderProduct)



    def get_product_by_sku(self, sku: str):
        stmt = select(InboundOrderProduct).join(Product, Product.id == InboundOrderProduct.id_product).where(Product.sku == sku)
        return db.session.scalar(stmt)

