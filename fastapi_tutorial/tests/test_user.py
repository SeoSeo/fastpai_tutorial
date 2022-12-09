import pytest


@pytest.mark.asyncio
async def test_get_empty_user(client):
    # 실제로는 유저가 생성되어 있지 않음. 인자로 안 받아왔으니까.
    r = await client.get("/users")
    # /users 를 엔드포인트로 요청 후 아래의 status code가 200 이면 정상으로 판단하는 것.
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_get_user(client, user):
    # 유저 있음.
    r = await client.get("/users")
    data = r.json()

    assert r.status_code == 200
    assert isinstance(data, list)
    assert data[0].get("username") == user.username


