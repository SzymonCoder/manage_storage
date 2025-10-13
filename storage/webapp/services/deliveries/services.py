#tutaj operacje usera co moze robic np. dodac produkt do bazy danych, albo admin usunac z bazy danych,
# fajnie byloby jeszcze zrobic zamowienie z produktow, ktore maja krotka date waznosci albo sa na wyczerpaniu
# stworzenie zamowienia i ustawianie statusow (nie ma wplywu na stan magazynowy
from ...database.repositories.suppliers import SupplierRepository
from ...database.repositories.warehouses import WarehouseRepository
from ...database.models.inbound_orders import InboundOrder, InboundOrderProduct, InboundOrderStatus
from ...database.models.products import Product


from ....webapp.database.repositories.inbound_orders import InboundOrderRepository
from ....webapp.database.repositories.stocks_summary import StockSummaryRepository
from ....webapp.database.repositories.stocks_with_exp_dates import StocksWithExpDateRepository
from ....webapp.database.repositories.stock_summary_arch import StockSummaryArchRepository
from ....webapp.database.repositories.stock_with_exp_dates_arch import StockWithExpDateArchRepository
from ....webapp.database.repositories.products_suppliers_info import ProductSupplierInfoRepository
from ....webapp.database.repositories.external_stock_repository import ExternalStockRepository
from ....webapp.database.repositories.products import ProductRepository
from ....webapp.database.repositories.inbound_order_product import InboundOrderProductRepository

from ....webapp.extensions import db

from ....webapp.services.extension import (
    ServiceException,
    NotFoundDataException,
    ValidationException,
)

from ..stock.service import StockService

from .mappers import inbound_order_to_dto


from storage.webapp.services.deliveries.dtos import (
    CreateInboundOrderDTO,
    UpdateQtySkuInboundOrderDTO,
    ReadInboundOrderDTO,
    AddProductToInboundOrderDTO,
    CreateOrderProductDTO,
    SetInboundOrderStatusDTO,
    UpdateQtySkuInboundOrderDTO,
    DeleteInboundOrderDTO,
    DeleteInboundOrderProductDTO

)



class InboundOrderService:
    def __init__(
            self,
            inbound_orders_repo: InboundOrderRepository,
            stocks_summary_repo: StockSummaryRepository,
            stocks_with_exp_dates_repo: StocksWithExpDateRepository,
            stock_summary_arch_repo: StockSummaryArchRepository,
            stock_with_exp_dates_arch_repo: StockWithExpDateArchRepository,
            product_supplier_info_repo: ProductSupplierInfoRepository,
            external_stock_repo: ExternalStockRepository,
            product_repo: ProductRepository,
            supplier_repo: SupplierRepository,
            warehouse_repo: WarehouseRepository,
            stock_service:StockService,
            inbound_order_product_repo: InboundOrderProductRepository
    ):
        self.inbound_orders_repo = inbound_orders_repo
        self.stocks_summary_repo = stocks_summary_repo
        self.stocks_with_exp_dates_repo = stocks_with_exp_dates_repo
        self.stock_summary_arch_repo = stock_summary_arch_repo
        self.stock_with_exp_dates_arch_repo = stock_with_exp_dates_arch_repo
        self.product_supplier_info_repo = product_supplier_info_repo
        self.external_stock_repo = external_stock_repo
        self.product_repo = product_repo
        self.supplier_repo = supplier_repo
        self.warehouse_repo = warehouse_repo
        self.stock_service = stock_service
        self.inbound_order_product_repo = inbound_order_product_repo






    def add_inbound_order(self, dto: CreateInboundOrderDTO) -> ReadInboundOrderDTO:
        with (db.session.begin()):
            if not self._check_supplier_active(dto.supplier_id):
                raise ServiceException('Supplier is not active')
            if not self._check_warehouse_active(dto.warehouse_id):
                raise ServiceException('Warehouse is not active')

            inbound_order = InboundOrder(
                warehouse_id=dto.warehouse_id,
                supplier_id=dto.supplier_id,
                status=InboundOrderStatus.CREATED
            )

            self.inbound_orders_repo.add(inbound_order)

        return inbound_order_to_dto(inbound_order)


#TODO : dokonczyc robienie dodawnai produktu do order po weryfikacji czy produkt jest aktywny.
    def add_product_to_inbound_order(self, dto: AddProductToInboundOrderDTO) -> ReadInboundOrderDTO:

        with db.session.begin():
            inbound_order = self._ensure_order(dto.order_id)
            self._add_item_internal(
                inbound_order,
                CreateOrderProductDTO(product_sku=dto.product_sku, quantity=dto.qty))

            return inbound_order_to_dto(inbound_order)




    def set_status(self, dto: SetInboundOrderStatusDTO) -> ReadInboundOrderDTO:
        new_status = self._status_from_literal(dto.status)

        with db.session.begin():
            order = self._ensure_order(dto.order_id)

            self._status_validation(order, new_status)

            self.inbound_orders_repo.edit_status(order, new_status)

            self.stock_service.update_stock_summary_inbound_order_qty(order.warehouse_id)

        return inbound_order_to_dto(order)


    def update_qty(self, dto: UpdateQtySkuInboundOrderDTO) -> ReadInboundOrderDTO:

        with db.session.begin():
            order = self._ensure_order(dto.order_id)
            for product in order.products:
                if product.product_sku == dto.sku:
                    old_qty = product.qty
                    self.inbound_orders_repo.edit_qty(product, dto.qty)

                    print(f"Product {dto.sku} updated from old qty = {old_qty} to new qty = {dto.qty}")
                    return inbound_order_to_dto(order)
            else:
                raise NotFoundDataException(f'Product {dto.sku} not found in order {dto.order_id}')



    def delete_order(self, dto: DeleteInboundOrderDTO) -> None:

        with db.session.begin():
            order = self._ensure_order(dto.inbound_order_id)
            if not order:
                raise NotFoundDataException(f'Order {dto.inbound_order_id} not found')
            elif order.status == InboundOrderStatus.COMPLETED:
                raise ValidationException(f'Order {dto.inbound_order_id} cannot be deleted due to COMPLETED status')
            else:
                self.inbound_orders_repo.delete_by_id(order.inbound_order_id)
                print(f"Order {dto.inbound_order_id} deleted")



    def delete_product_in_order(self, dto: DeleteInboundOrderProductDTO) -> None:

        with db.session.begin():
            order = self._ensure_order(dto.inbound_order_id)
            product = self._ensure_product(dto.product_sku)
            if not order:
                raise NotFoundDataException(f'Order {dto.inbound_order_id} not found')
            if not product:
                raise NotFoundDataException(f'Product {dto.product_sku} not found in order {dto.inbound_order_id}')

            inbound_order_product = next(
                (p for p in order.inbound_order_products if p.product_id == product.id),
                None
            )

            if not inbound_order_product:
                raise NotFoundDataException(
                    f"Product {dto.product_sku} is not associated with order {dto.inbound_order_id}")

            db.session.delete(inbound_order_product)






    # zawsze przy dodaniu albo aktualizacji zamowienie trzeba wykorzystac z StockService -> update_stock_summary_inbound_order_qty


    def _check_supplier_active(self, supplier_id: int) -> bool:
        return bool(self.supplier_repo.get_by_id(supplier_id).is_active)

    def _check_warehouse_active(self, warehouse_id: int) -> bool:
        return bool(self.warehouse_repo.get_by_id(warehouse_id).is_active)

    def _check_product_active(self, product_sku: str) -> bool:
        return bool(self.product_repo.get_by_sku(product_sku).is_active)



    def _ensure_order(self, order_id: int) -> InboundOrder:
        order = self.inbound_orders_repo.get(order_id)

        if not order:
            raise NotFoundDataException(f'Order {order_id} not found')

        return order

    def _ensure_product(self, product_sku: str) -> Product:
        product = self.product_repo.get_by_sku(product_sku)
        if not product:
            raise NotFoundDataException(f'Product {product_sku} not found')
        if not product.is_active:
            raise ValidationException(f'Product {product_sku} is not active')

        return product




    def _add_item_internal(self, inbound_order: InboundOrder, product_dto: CreateOrderProductDTO) -> InboundOrderProduct:
        product = self._ensure_product(product_dto.product_sku)
        supplier_check = self.supplier_repo.get_by_id(inbound_order.supplier_id)

        if not supplier_check.is_active:
            raise ServiceException(f'Supplier {inbound_order.supplier_id} does not support this product')

        return self.inbound_orders_repo.add_product_to_inbound_order(
            order=inbound_order,
            product_id=product.id,
            qty=product_dto.quantity

        )


    def _status_from_literal(self, status: str) -> InboundOrderStatus:
        try:
            return InboundOrderStatus(status)
        except ValueError:
            raise ValidationException(f'Invalid status {status}')


    def _status_validation(self, inbound_order: InboundOrder, new_status: InboundOrderStatus) -> None:

        current_status = InboundOrderStatus(inbound_order.status)
        """
        Waliduje, czy przejście statusu zamówienia jest zgodne z dozwolonymi regułami:
        - Przejście od CREATED -> APPROVED -> PRODUCED -> IN_TRANSIT -> DELIVERED -> COMPLETED.
        - Z każdego statusu można przejść do CANCELED.
        - Z CANCELED nie można przejść do żadnego innego statusu.
        """
        # Definicja dozwolonych przejść statusu
        allowed_transitions = {
            InboundOrderStatus.CREATED: [InboundOrderStatus.APPROVED, InboundOrderStatus.CANCELLED],
            InboundOrderStatus.APPROVED: [InboundOrderStatus.PRODUCED, InboundOrderStatus.CANCELLED],
            InboundOrderStatus.PRODUCED: [InboundOrderStatus.IN_TRANSIT, InboundOrderStatus.CANCELLED],
            InboundOrderStatus.IN_TRANSIT: [InboundOrderStatus.DELIVERED, InboundOrderStatus.CANCELLED],
            InboundOrderStatus.DELIVERED: [InboundOrderStatus.COMPLETED, InboundOrderStatus.CANCELLED],
            InboundOrderStatus.COMPLETED: [InboundOrderStatus.CANCELLED],
            InboundOrderStatus.CANCELLED: []  # Brak dalszych przejść
        }

        # Sprawdzanie, czy przejście jest dozwolone
        if new_status not in allowed_transitions[current_status]:
            raise ValidationException(
                f"Status cannot be changed from '{current_status.value}' to '{new_status.value}'. "
                f"Allowed changes: {[status.value for status in allowed_transitions[current_status]]}"
            )
