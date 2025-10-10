from sqlalchemy import select, func
from ...extensions import db
from ..models.inbound_orders import InboundOrder, InboundOrderStatus, InbounOrderProduct
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


    def add_product_to_inbound_order(self, order: InboundOrder, product_id: int, qty: int) -> InbounOrderProduct:
        product = InbounOrderProduct(
            inbound_order_id=order.id,
            product_id=product_id,
            qty=qty
        )
        db.session.add(product)
        return product



# ------------------------ Filtry ------------------------

    def get_by_supplier(self, supplier_name: str) -> list[InboundOrder] | None:
        stmt = select(InboundOrder).where(InboundOrder.supplier_name.is_(supplier_name))
        return list(db.session.scalars(stmt))

    def get_by_sku(self, sku: str) -> list[InboundOrder] | None:
        stmt = select(InboundOrder).where(InboundOrder.sku.is_(sku))
        return list(db.session.scalars(stmt))

    def get_qty_by_active_orders_by_sku(self, sku: str, warehouse_id: int) -> int | None:
        product_id = self.get_by_sku(sku)[0].product_id
        active_orders = self.get_active_ordered_quantities(warehouse_id)
        return active_orders.get(product_id)

    def get_active_ordered_quantities(self, warehouse_id: int) -> dict:
        active_statuses = [
            status for status in InboundOrderStatus
            if status not in (InboundOrderStatus.CANCELLED, InboundOrderStatus.COMPLETED)
        ]

        stmt = (
            select(
                InboundOrder.product_id,
                func.sum(InboundOrder.quantity).label("total_ordered")
            )
            .where(
                InboundOrder.warehouse_id == warehouse_id,
                InboundOrder.status.in_(active_statuses)
            )
            .group_by(InboundOrder.product_id)
        )

        result = db.session.execute(stmt)

        return {row.product_id: row.total_ordered for row in result}
