#tutaj operacje usera co moze robic np. dodac produkt do bazy danych, albo admin usunac z bazy danych,
# fajnie byloby jeszcze zrobic zamowienie z produktow, ktore maja krotka date waznosci albo sa na wyczerpaniu
# stworzenie zamowienia i ustawianie statusow (nie ma wplywu na stan magazynowy
from ...database.repositories.suppliers import SupplierRepository
from ...database.repositories.warehouses import WarehouseRepository
from ....webapp.database.models.inbound_orders import InboundOrder, InbounOrderProduct, InboundOrderStatus


from ....webapp.database.repositories.inbound_orders import InboundOrderRepository
from ....webapp.database.repositories.stocks_summary import StockSummaryRepository
from ....webapp.database.repositories.stocks_with_exp_dates import StocksWithExpDateRepository
from ....webapp.database.repositories.stock_summary_arch import StockSummaryArchRepository
from ....webapp.database.repositories.stock_with_exp_dates_arch import StockWithExpDateArchRepository
from ....webapp.database.repositories.products_suppliers_info import ProductSupplierInfoRepository
from ....webapp.database.repositories.external_stock_repository import ExternalStockRepository
from ....webapp.database.repositories.products import ProductRepository

from ....webapp.extensions import db

from ....webapp.services.extension import (
    ServiceException,
    NotFoundDataException,
    ValidationException,
)

from .mappers import inbound_order_to_dto


from storage.webapp.services.deliveries.dtos import CreateInboundOrderDTO, UpdateInboundOrderDTO, ReadInboundOrderDTO



class DeliveryService:
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
    def add_product_to_inbound_order(self, dto: AddProductToInboundOrderDTO) -> None:

        with db.session.begin():
            order = self._ensure_order(dto.order_id)
            self._add_item_internal(
                order,
                CreateOrderItemDTO(
                    product_id=dto.product_id,
                    quantity=dto.quantity,
                    unit_price=dto.unit_price,
                )
            )
            return inbound_order_to_dto(order)




    def update_inbound_order(self, dto: UpdateInboundOrderDTO) -> ReadInboundOrderDTO:
        pass



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