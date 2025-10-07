from typing import Iterable
from sqlalchemy import select
from flask_sqlalchemy.model import Model
from ...extensions import db


class GenericRepository[T: Model]:
    def __init__(self, model: type[T]):
        self.model = model


    def add(self, ):