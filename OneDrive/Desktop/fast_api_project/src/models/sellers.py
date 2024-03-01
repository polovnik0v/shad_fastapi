from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType
from .base import BaseModel
from src.models.books import Book
from typing import List


class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(EmailType, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    books: Mapped[List["Book"]] = relationship(cascade="all, delete-orphan")  # noqa F821

