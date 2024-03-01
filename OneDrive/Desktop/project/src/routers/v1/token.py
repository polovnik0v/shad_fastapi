from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.sellers import Seller
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import IncomingData
from src.utils.passwords import verify_password, create_access_token

token_router = APIRouter(tags=["token"], prefix="/token")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@token_router.post("/", status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def login_for_access_token(data: IncomingData, session: DBSession):
    email = data.email
    password = data.password
    seller = await session.execute(
        select(Seller).where(Seller.email == email)
    )
    seller = seller.scalars().first()
    if not seller or not verify_password(password, seller.password):
        return Response(status_code=status.HTTP_401_UNAUTHORIZED,
                        content="Incorrect email or password")
    access_token = create_access_token(data={"sub": email})

    return {"token": access_token}
