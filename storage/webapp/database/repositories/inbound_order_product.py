from sqlalchemy import select, func
from ...extensions import db
from ..models.inbound_orders import InboundOrder, InboundOrderStatus, InboundOrderProduct
from .generic import GenericRepository


class InboundOrderProductRepository(GenericRepository[InboundOrderProduct]):
    def __init__(self):
        super().__init__(InboundOrderProduct)



    def get_product_by_sku(self, sku: str):
        stmt = select(InboundOrderProduct).where(InboundOrderProduct.sku.is_(sku))
        return db.session.scalar(stmt)

