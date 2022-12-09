import pytest
from httpx import AsyncClient
# from fastapi.testclient import TestClient # 사용 안 하는 이유 : 비동기 테스트 불가.

# app 에서 상속.
from app import main, models
from app.database import engine, get_db
from app.config import settings


@pytest.fixture(scope="session")
def app():
    # 잘못되면 Error 뱉어서 올리기. 개발서버에 접근 차단.
    if not settings.TESTING:
        raise SystemError("TESTING environment must be set true!!")
    return main.app

# @pytest.fixture 함수 안에 인자로 넘기는 방법으로 쓴다고 함.


@pytest.fixture
async def session():
    # dependency 때문.
    db = next(get_db())
    # db = await get_db()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def default_client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test/v1") as ac:
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        yield ac
# Base = declarative_base() in fastapi_tutorial/app/database.py


# user 추가하여 testing
@pytest.fixture
def user(session) -> models.User:
    row = models.User(username="fc2021", first_name="Fast", last_name="Campus")
    session.add(row)
    session.commit()

    return row


# test_quiz.py 등
@pytest.fixture
def add_quiz(session):
    def func(question: str = None, content: str = None, answer: int = None) -> models.Quiz:
        r = models.Quiz(
            # or 는 아무런 질문도 하지 않을 경우 대비 즉 빈칸 대비용.
            question=question or "Question!",
            content=content or "Content Text!",
            answer=answer or 1,
        )
        session.add(r)
        session.commit()
        return r

    return func


# mocking 추가
@pytest.fixture(autouse=True)
# @pytest.mark.asyncio  # 추가
async def mock_telegram(monkeypatch):
    from app.lib.telegram import Telegram

    async def mock_get_bot_info(*args, **kwargs):
        ...

    async def mock_get_webhook(*args, **kwargs):
        return {
            "ok": True,
            "result": {
                "has_custom_certificate": False,
                "ip_address": "127.0.0.1",
                "last_error_date": 1622887352,
                "last_error_message": "Wrong response from the webhook: 500 Internal Server Error",
                "max_connections": 40,
                "pending_update_count": 0,
                "url": "https://localhost/v1/webhook/sometoken",
            },
        }

    async def mock_set_webhook(*args, **kwargs):
        return {"OK": True, "result": True, "description": "Webhook is already set!"}

    async def mock_send_message(*args, **kwargs):
        return {
            "message_id": 1234,
            "from": {
                "id": 123,
                "is_bot": False,
                "first_name": "first",
                "last_name": "last",
                "username": "username",
                "language_code": "ko",
            },
            "chat": {
                "id": 123,
                "type": "private",
                "first_name": "first",
                "last_name": "last",
                "username": "username",
            },
            "datetime": 1622902229,
            "text": "some text",
        }

    monkeypatch.setattr(Telegram, "get_bot_info", mock_get_bot_info)
    monkeypatch.setattr(Telegram, "get_webhook", mock_get_webhook)
    monkeypatch.setattr(Telegram, "set_webhook", mock_set_webhook)
    monkeypatch.setattr(Telegram, "send_message", mock_send_message)

