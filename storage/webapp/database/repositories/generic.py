from typing import Iterable
from sqlalchemy import select
from flask_sqlalchemy.model import Model
from ...extensions import db
from abc import ABC


class GenericRepository[T: Model]:
    def __init__(self, model: type[T]):
        self.model = model

    # ----------------------- Sekcja do niejawnego wykorzystania funkcji - potrzebny commit -----------------------

    def add(self, instance: T) -> T:
        db.session.add(instance)
        return instance

    def add_many(self, instance: Iterable[T]) -> None:
        return db.session.add_all(list(instance))

    def delete(self, instance: T) -> None:
        return db.session.delete(instance)

    def delete_by_id(self, pk: int) -> None:
        obj = db.session.get(self.model, pk)
        if obj:
            db.session.delete(obj)

    def get(self, pk: int) -> T | None:
        return db.session.get(self.model, pk)

    def get_all(self) -> list[T]:
        objects = select(self.model)
        return list(db.session.scalars(objects).all())

    # ----------------------- Jawne sterowanie transakcjami -----------------------

    def commit(self) -> None:
        return db.session.commit()

    def rollback(self) -> None:
        return db.session.rollback()

    # funkcja flush wysyla dane do bazy danych, ale mimo wszystko jeszcze nie zatwierdza ich w bazie
    # mozan je potwierdzic albo cofnac
    def flush(self) -> None:
        return db.session.flush()

    def refresh(self, instance: T) -> None:
        return db.session.refresh(instance)

    # ----------------------- Sekcja funkcji z commitami -----------------------

    def add_and_commit(self, instance: T) -> T:
        db.session.add(instance)
        db.session.commit()
        return instance

    def delete_and_commit(self, instance: T) -> None:
        db.session.delete(instance)
        db.session.commit()

