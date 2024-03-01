from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.models.books import Book
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks
from src.utils.passwords import get_password_hash
from src.utils.decorators import protect_with_token

sellers_router = APIRouter(tags=["seller"], prefix="/seller")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller,
                     status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
        seller: IncomingSeller, session: DBSession
):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=get_password_hash(seller.password),
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
@protect_with_token
async def get_seller(seller_id: int, session: DBSession):
    seller_res = await session.get(Seller, seller_id)
    if not seller_res:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    books_res = await session.execute(select(Book).where(Book.seller_id == seller_id))
    returned_value = {
        "id": seller_res.id,
        "first_name": seller_res.first_name,
        "last_name": seller_res.last_name,
        "email": seller_res.email,
        "books":  books_res.scalars().all()
    }

    return returned_value


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.