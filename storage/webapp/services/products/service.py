from webapp.database.repositories import ProductRepository

from webapp.services.extension import (
    ServiceException,
    NotFoundDataException,
    ValidationException,

)



class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo



