from sqlalchemy import select, func

from ..models.products import Product
from ..models.suppliers import Supplier
from ...extensions import db
from ..models.inbound_orders import InboundOrder, InboundOrderStatus, InboundOrderProduct
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


    def add_product_to_inbound_order(self, order: InboundOrder, product_id: int, qty: int) -> InboundOrderProduct:
        product = InboundOrderProduct(
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

    def get_active_ordered_quantities(self, warehouse_id: int) -> dict[str, int]:
        orders_with_products = self.get_inbound_orders_with_products(warehouse_id)
        if not orders_with_products:
            return {}

        active_orders_qty = {}

        for order in orders_with_products:
            if order['sku'] not in active_orders_qty:
                active_orders_qty[order['sku']] = order['product_qty']
            else:
                active_orders_qty[order['sku']] += order['product_qty']

        return active_orders_qty


    def get_qty_of_ordered_in_product(self, warehouse_id: int, sku_look: str) -> int | None:
        all_active_inbound_orders = self.get_active_ordered_quantities(warehouse_id)
        for sku, qty in all_active_inbound_orders.items():
            if sku == sku_look:
                return qty
        return 0

    def get_inbound_orders_with_products(
            self,
            warehouse_id: int | None = None,
            statuses: list[InboundOrderStatus] | None = None
    ) -> list[dict]:
        """
        Zwraca listę produktów z zamówień przychodzących wraz z informacjami o zamówieniu.
        Można filtrować po magazynie (warehouse_id) i statusie (pojedynczym lub wielu).

        - Jeśli `warehouse_id` = None → zwraca wszystkie magazyny.
        - Jeśli `statuses` = None → zwraca tylko aktywne (czyli wszystko oprócz CANCELLED i DRAFT).
        """

        # Domyślnie tylko aktywne zamówienia
        active_statuses = [
            status for status in InboundOrderStatus
            if status not in (InboundOrderStatus.CANCELLED, InboundOrderStatus.CREATED)
        ]

        selected_statuses = statuses or active_statuses

        stmt = (
            select(
                InboundOrderProduct.id.label("inbound_order_product_id"),
                InboundOrderProduct.inbound_order_id,
                InboundOrderProduct.product_id,
                InboundOrderProduct.quantity.label("product_qty"),
                Supplier.name.label("supplier_name"),
                InboundOrder.status,
                InboundOrder.warehouse_id,
                InboundOrder.created_at,
                Product.sku
            )
            .join(InboundOrder, InboundOrder.id == InboundOrderProduct.inbound_order_id)
            .join(Product, InboundOrderProduct.product_id == Product.id)
            .where(InboundOrder.status.in_(selected_statuses))
        )

        # Opcjonalny filtr po magazynie
        if warehouse_id is not None:
            stmt = stmt.where(InboundOrder.warehouse_id == warehouse_id)

        stmt = stmt.order_by(InboundOrder.id)

        result = db.session.execute(stmt)

        return [
            {
                "inbound_order_product_id": row.inbound_order_product_id,
                "inbound_order_id": row.inbound_order_id,
                "product_id": row.product_id,
                "product_qty": row.product_qty,
                "supplier_name": row.supplier_name,
                "status": row.status,
                "warehouse_id": row.warehouse_id,
                "created_at": row.created_at,
                "sku": row.sku
            }
            for row in result
        ]