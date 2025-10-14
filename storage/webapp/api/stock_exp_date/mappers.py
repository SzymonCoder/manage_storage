from ..stock_exp_date.schemas import ReadStockExpDateSchema


from ....webapp.services.stock.dtos import ReadStockExpDateDTO





def to_schema_dto_read_stock_with_exp_date(dto: ReadStockExpDateDTO) -> ReadStockExpDateSchema:
    return ReadStockExpDateSchema(
        warehouse_id=dto.warehouse_id,
        product_id=dto.product_id,
        expiration_date=dto.expiration_date,
        qty_per_exp_date=dto.qty_per_exp_date,
        qty_total_of_sku=dto.qty_total_of_sku,
        status_of_exp_date=dto.status_of_exp_date,
        status_of_total_qty=dto.status_of_total_qty
    )



