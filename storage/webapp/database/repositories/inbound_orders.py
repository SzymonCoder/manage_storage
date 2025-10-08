from sqlalchemy import select
from ...extensions import db
from ..models.inbound_orders import InboundOrder, InboundOrderStatus
from .generic import GenericRepository


class InboundOrderRepository(GenericRepository[InboundOrder]):
    def __init__(self):
        super().__init__(InboundOrder)

# ------------------------ Aktualizacje statusow i opisu ------------------------


    def edit_status(self, order: InboundOrder, status: InboundOrderStatus) -> None:
        order.status = status

    def edit_qty(self, order: InboundOrder, qty: int) -> None:
        order.qty = qty

    def edit_product_id(self, order: InboundOrder, product_id: int) -> None:
        order.product_id = product_id



# ------------------------ Filtry ------------------------

    def get_by_supplier(self, supplier_name: str) -> list[InboundOrder] | None:
        stmt = select(InboundOrder).where(InboundOrder.supplier_name.is_(supplier_name))
        return list(db.session.scalars(stmt))

    def get_by_sku(self, sku: str) -> list[InboundOrder] | None:
        stmt = select(InboundOrder).where(InboundOrder.sku.is_(sku))
        return list(db.session.scalars(stmt))