import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books
from src.models import sellers
from src.utils.passwords import create_access_token

# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    data = {"first_name": "1", "last_name": "1", "email": "123@mail.com", "password": "123123123123"}
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "first_name": "1",
        "last_name": "1",
        "email": "123@mail.com"
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller1 = sellers.Seller(first_name="1", last_name="2", email="123@email.com",
                              password="1231231231")
    seller2 = sellers.Seller(first_name="12", last_name="22", email="123@email.com",
                              password="123123123123")

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [{"id": seller1.id, "first_name": "1", "last_name": "2", "email": "123@email.com"},
                    {"id": seller2.id, "first_name": "12", "last_name": "22", "email": "123@email.com"},
                    ]
    }



@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):

    seller = sellers.Seller(first_name="123", last_name="123", email="123@email.com",
                             password="123123123123123")
    db_session.add(seller)
    await db_session.flush()
    token = create_access_token(data={"sub": seller.email})

    data = {"token": token, "title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007,
            "seller_id": seller.id}
    response = await async_client.post("/api/v1/books/", json=data)

    result_data = response.json()
    response = await async_client.request(method="GET", url=f"/api/v1/seller/{seller.id}", content="{" + f"\"token\":\"{str(token)}\"" + "}")

    assert response.status_code == status.HTTP_200_OK
    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {"id": seller.id,
                               "first_name": "123",
                               "last_name": "123",
                               "email": "123@email.com",
                               "books": [result_data]
                               }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="Vasya", last_name="Onegin", email="123@email.com,",
                             password="password123123")

    db_session.add(seller)
    await db_session.flush()
    # добавим книги продавцу
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0

    all_seller_books = await db_session.execute(select(books.Book).where(books.Book.seller_id == seller.id))
    res = all_seller_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="Pushkin", last_name="Pushkin", email="123@email.com",
                             password="123123123123312")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={"first_name": "vasya", "last_name": "Pushkin", "email": "123@mail.com", "id": seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "vasya"
    assert res.last_name == "Pushkin"
    assert res.email == "123@mail.com"
    assert res.id == seller.id



