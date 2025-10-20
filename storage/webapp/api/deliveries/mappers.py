from .schemas import (
    CreateInboundOrderSchema,
    InboundOrderResponseSchema,
    AddProductToInboundOrderSchema,
    SetInboundOrderStatusSchema,
    UpdateQtySkuInboundOrderSchema,
    DeleteInboundOrderProductSchema,
    ReadInboundOrderProductsWithOrderSchema

)
from ...services.deliveries.dtos import (
    CreateInboundOrderDTO,
    ReadInboundOrderDTO,
    AddProductToInboundOrderDTO,
    SetInboundOrderStatusDTO,
    UpdateQtySkuInboundOrderDTO,
    DeleteInboundOrderDTO,
    DeleteInboundOrderProductDTO,
    ReadInboundOrderProductsWithOrderDTO
)





def to_dto_order_inbound(schema: CreateInboundOrderSchema) -> CreateInboundOrderDTO:
    return CreateInboundOrderDTO(
        warehouse_id=schema.warehouse_id,
        supplier_id=schema.supplier_id
    )


def to_schema_dto_order_inbound(dto: ReadInboundOrderDTO) -> InboundOrderResponseSchema:
    return InboundOrderResponseSchema(
        inbound_order_id=dto.inbound_order_id,
        warehouse_id=dto.warehouse_id,
        supplier_id=dto.supplier_id,
        status=dto.status
    )

def to_dto_add_product_to_order(schema: AddProductToInboundOrderSchema) -> AddProductToInboundOrderDTO:
    return AddProductToInboundOrderDTO(
        order_id=schema.order_id,
        product_sku=schema.product_sku,
        qty=schema.qty
    )

def to_dto_update_status_order(schema: SetInboundOrderStatusSchema) -> SetInboundOrderStatusDTO:
    return SetInboundOrderStatusDTO(
        order_id=schema.order_id,
        status=schema.status
    )


def to_dto_update_qty_sku(schema: UpdateQtySkuInboundOrderSchema) -> UpdateQtySkuInboundOrderDTO:
    return UpdateQtySkuInboundOrderDTO(
        order_id=schema.order_id,
        sku=schema.sku,
        qty=schema.qty
    )

def to_dto_delete_order(inbound_order_id: int) -> DeleteInboundOrderDTO:
    return DeleteInboundOrderDTO(
        inbound_order_id=inbound_order_id
    )

def to_dto_delete_order_product(schema: DeleteInboundOrderProductSchema) -> DeleteInboundOrderProductDTO:
    return DeleteInboundOrderProductDTO(
        inbound_order_id=schema.inbound_order_id,
        product_sku=schema.product_sku
    )


def to_schema_dto_inbound_order_with_products(dto: ReadInboundOrderProductsWithOrderDTO) -> ReadInboundOrderProductsWithOrderSchema:
    return ReadInboundOrderProductsWithOrderSchema(
            warehouse_id=dto.warehouse_id,
            inbound_order_id=dto.inbound_order_id,
            inbound_order_product_id=dto.inbound_order_product_id,
            product_id=dto.product_id,
            product_qty=dto.product_qty,
            supplier_name=dto.supplier_name,
            status=dto.status
            )

