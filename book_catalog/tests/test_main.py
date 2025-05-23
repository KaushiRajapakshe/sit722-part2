import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from book_catalog.main import app, get_db
from book_catalog.models import Book, Base

# Use your existing development database (be careful!)
SQLALCHEMY_DATABASE_URL = "postgresql://book_catalog_l1mv_user:HMb59Hj8vzIgb3IyLtQTKy9rQ0bN8lDy@dpg-d0ns64buibrs73c4dacg-a.singapore-postgres.render.com/book_catalog_l1mv"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_test_books():
    # Code before the test (nothing)
    yield
    # Cleanup: Remove books with title containing "[TEST]"
    db = TestingSessionLocal()
    db.query(Book).filter(Book.title.contains("[TEST]")).delete()
    db.commit()
    db.close()

def test_create_book():
    response = client.post("/books/", json={"title": "[TEST] Book", "author": "Tester", "year": 2020})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "[TEST] Book"
    assert data["author"] == "Tester"
    assert data["year"] == 2020
    assert "id" in data

def test_get_book():
    post = client.post("/books/", json={"title": "[TEST] Book2", "author": "B", "year": 2021})
    book_id = post.json()["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "[TEST] Book2"

def test_get_all_books():
    client.post("/books/", json={"title": "[TEST] Book3", "author": "A1", "year": 2019})
    client.post("/books/", json={"title": "[TEST] Book4", "author": "A2", "year": 2018})
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    # There may be many books—just check at least 2 with "[TEST]" in title
    test_books = [b for b in data if "[TEST]" in b["title"]]
    assert len(test_books) >= 2

def test_update_book():
    post = client.post("/books/", json={"title": "[TEST] Old", "author": "O", "year": 2010})
    book_id = post.json()["id"]
    response = client.put(f"/books/{book_id}", json={"title": "[TEST] New", "author": "N", "year": 2022})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "[TEST] New"
    assert data["author"] == "N"
    assert data["year"] == 2022

def test_delete_book():
    post = client.post("/books/", json={"title": "[TEST] Del", "author": "A", "year": 2005})
    book_id = post.json()["id"]
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200
    # Confirm deletion
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404
