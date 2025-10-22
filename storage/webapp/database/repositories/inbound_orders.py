from typing import Optional, List

from sqlalchemy import select

from .generic import GenericRepository
from ..models.inbound_orders import InboundOrder, InboundOrderStatus, InboundOrderProduct
from ..models.products import Product
from ..models.suppliers import Supplier
from ...extensions import db


class InboundOrderRepository(GenericRepository[InboundOrder]):
    def __init__(self):
        super().__init__(InboundOrder)

# ------------------------ Aktualizacje statusow i opisu ------------------------


    def edit_status(self, order: InboundOrder, status: InboundOrderStatus) -> None:
        order.status = status

    def edit_qty(self, order_id: int, sku: str, qty: int) -> None:
        products = self.get_inbound_order_with_products(order_id)
        product_id = self._get_product_id_by_sku(sku)

        for product in products:
            if product.product_id == product_id:
                product.quantity = qty
            else:
                raise Exception(f"Product {sku} not found in order {order_id}")



    def edit_product_id(self, order: InboundOrder, product_id: int) -> None:
        order.product_id = product_id

    def add_product_to_inbound_order(self, order: InboundOrder, product_id: int, qty: int) -> InboundOrderProduct:
        order_with_products = self.get_inbound_order_with_products(order.id)

        # Szukamy produktu w istniejących pozycjach
        for product in order_with_products:
            if product.product_id == product_id:
                # Nadpisujemy ilość, jeśli produkt już istnieje
                product.quantity = qty
                db.session.add(product)
                return product

        # Jeśli nie znaleziono produktu — dodajemy nowy
        new_product = InboundOrderProduct(
            inbound_order_id=order.id,
            product_id=product_id,
            quantity=qty
        )
        db.session.add(new_product)
        return new_product



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



    def get_inbound_order_with_products(
            self,
            order_id: int,
    ) -> list[InboundOrderProduct]:
        stmt = select(InboundOrderProduct).where(InboundOrderProduct.inbound_order_id == order_id)
        return db.session.scalars(stmt)

    def get_inbound_orders_with_products(
        self,
        warehouse_id: Optional[int] = None,
        statuses: Optional[List[InboundOrderStatus]] = None
    ) -> List[dict]:

        active_statuses = [s for s in InboundOrderStatus if s.name not in ("CANCELLED", "CREATED")]
        selected_statuses = statuses or active_statuses

        stmt = (
            select(
                InboundOrder.id.label("inbound_order_id"),
                InboundOrder.status.label("status"),
                InboundOrder.warehouse_id.label("warehouse_id"),
                InboundOrder.created_at.label("created_at"),
                Supplier.name.label("supplier_name"),
                InboundOrderProduct.id.label("inbound_order_product_id"),
                InboundOrderProduct.product_id.label("product_id"),
                InboundOrderProduct.quantity.label("product_qty"),
                Product.sku.label("sku")
            )
            .select_from(InboundOrder)
            .join(InboundOrderProduct, InboundOrderProduct.inbound_order_id == InboundOrder.id, isouter=True)
            .join(Product, InboundOrderProduct.product_id == Product.id, isouter=True)
            .join(Supplier, Supplier.id == InboundOrder.supplier_id, isouter=True)
            .where(InboundOrder.status.in_(selected_statuses))
        )

        if warehouse_id is not None:
            stmt = stmt.where(InboundOrder.warehouse_id == warehouse_id)

        stmt = stmt.order_by(InboundOrder.id)
        result = db.session.execute(stmt).all()

        orders_list = []
        for row in result:
            orders_list.append(dict(row._mapping))
        return orders_list





    def _get_product_id_by_sku(self, sku: str) -> int | None:
        stmt = select(Product.id).where(Product.sku == sku)
        return db.session.scalar(stmt)