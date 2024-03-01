import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books
from src.models import sellers
from src.utils.passwords import create_access_token
result = {
    "books": [
        {"author": "fdhgdh", "title": "jdhdj", "year": 1997},
        {"author": "fdhgdfgfrh", "title": "jrrgdhdj", "year": 2001},
    ]
}


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    seller = sellers.Seller(first_name="1", last_name="2", email="sss@email.com,", password="11111111111")
    db_session.add(seller)

    await db_session.flush()
    token = create_access_token(data={"sub": seller.email})

    data = {"token":token, "title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007, "seller_id": seller.id}
    response = await async_client.post("/api/v1/books/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "title": "Wrong Code",
        "author": "Robert Martin",
        "count_pages": 104,
        "year": 2007,
        "seller_id": 1
    }


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    seller = sellers.Seller(first_name="1", last_name="2", email="sss@email.com,", password="11111111111")
    db_session.add(seller)
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="P", title="EP", year=2001, count_pages=100, seller_id=seller.id)
    book_2 = books.Book(author="L", title="L", year=1997, count_pages=1000, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) >= 2

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {"title": "EP", "author": "P", "year": 2001, "id": book.id, "count_pages": 100, "seller_id": seller.id},
            {"title": "L", "author": "L", "year": 1997, "id": book_2.id, "count_pages": 1000, "seller_id": seller.id},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="1", last_name="2", email="sss@email.com,", password="11111111111")
    db_session.add(seller)
    await db_session.flush()

    book = books.Book(author="P", title="EP", year=2001, count_pages=100, seller_id=seller.id)
    book_2 = books.Book(author="L", title="L", year=1997, count_pages=1000, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "EP",
        "author": "P",
        "year": 2001,
        "count_pages": 100,
        "id": book.id,
        "seller_id": seller.id
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="1", last_name="2", email="sss@email.com,", password="11111111111")
    db_session.add(seller)
    await db_session.flush()
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=100, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="1", last_name="2", email="sss@email.com", password="11111111111")
    db_session.add(seller)
    await db_session.flush()

    token = create_access_token(data={"sub": seller.email})

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=100, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"token":token, "title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007, "id": book.id,
              "seller_id": seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.id == book.id
    assert res.seller_id == seller.id
