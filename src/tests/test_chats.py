import pytest
from tests.conftest import session_factory
from messenger.database.models import ChatORM, UserORM
from sqlalchemy import or_, and_, select



# ======================================================================
# ====================== GET CHATS (GET) ===============================
# ======================================================================

# ========================================= Test Get User Chat =========================================
@pytest.mark.parametrize(
        "user_id",
        [0, 1]
)
@pytest.mark.asyncio
async def test_get_user_chat(create_test_users, create_test_chat, get_client, user_id):
    users = await create_test_users(2)
    chat = await create_test_chat(
        users[0]["id"],
        users[1]["id"]
    )

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[user_id]["email"],
            "password": users[user_id]["password"]
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get("/api/chats/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["chat_id"] == chat["chat_id"]
    assert data[0]["recipient_username"] == users[1 - user_id]["username"]

# ========================================= User no Chats =========================================
@pytest.mark.asyncio
async def test_get_user_no_chats(create_test_users, get_client):
    users = await create_test_users(1)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]["email"],
            "password": users[0]["password"]
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get("/api/chats/")
    data = response.json()

    assert response.status_code == 200
    assert data == []

# ========================================= Multiple Chats =========================================
@pytest.mark.asyncio
async def test_get_user_multiple_chats(create_test_users, create_test_chat, get_client):
    users = await create_test_users(4)

    chat_1 = await create_test_chat(users[0]["id"], users[1]["id"])
    chat_2 = await create_test_chat(users[2]["id"], users[0]["id"])

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]["email"],
            "password": users[0]["password"]
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get("/api/chats/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    usernames = [item["recipient_username"] for item in data]

    assert set(usernames) == {
        users[1]["username"],
        users[2]["username"]
    }

# ========================================= Unauthorized request =========================================
@pytest.mark.asyncio
async def test_unauthorized_request(get_client):
    response = await get_client.get("/api/chats/")

    assert response.status_code == 401

    data = response.json()

    assert data["detail"]["error"] == "not_authenticated"

# =================== Test Specific User - Specific Chats ===================
@pytest.mark.asyncio
async def test_specific_user_has_own_chats(get_client, create_test_users, create_test_chat):
    users = await create_test_users(4)
    chat_1 = await create_test_chat(users[0]["id"], users[1]["id"])
    chat_2 = await create_test_chat(users[2]["id"], users[3]["id"])

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]["email"],
            "password": users[0]["password"]
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get("/api/chats/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["chat_id"] == chat_1["chat_id"]
    assert data[0]["recipient_username"] == users[1]["username"]

# ======================================================================
# ====================== SEARCH USER (GET) =============================
# ======================================================================

# ============================== Test user found ==============================
@pytest.mark.asyncio
async def test_search_user_found(get_client, create_test_users):
    users = await create_test_users(2)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]["email"],
            "password": users[0]["password"]
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(
        "/api/users/search/",
        params={"username": users[1]["username"]}
    )

    assert response.status_code == 200

    data = response.json()

    assert data['user_id'] == users[1]['id']
    assert data['username'] == users[1]['username']

# ============================== Test User not found ==============================
@pytest.mark.asyncio
async def test_search_user_not_found(get_client, create_test_users):
    users = await create_test_users(1)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(
        "/api/users/search/",
        params={"username": "fake_username"}
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail']['error'] == "not_found"
    assert data['detail']['message'] == "User not found"

# ============================== Test self search ==============================
@pytest.mark.asyncio
async def test_search_user_search_yourself(get_client, create_test_users):
    users = await create_test_users(1)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(
        "/api/users/search/",
        params={"username": users[0]['username']}
    )

    assert response.status_code == 400

    data = response.json()

    assert data['detail']['error'] == "self_search"
    assert data['detail']['message'] == "You can't search for yourself"

# ============================== Test search not-authorized ==============================
@pytest.mark.asyncio
async def test_search_user_not_authorized(get_client):
    response = await get_client.get(
        "/api/users/search/",
        params={"username": "my_username"}
    )

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "not_authenticated"
    assert data['detail']['message'] == "Not authenticated"

# ======================================================================
# ====================== CREATE NEW CHAT OR GET EXISTING ONE (POST) ====
# ======================================================================

# ================================ Test create new chat ================================
@pytest.mark.asyncio
async def test_create_new_chat(get_client, create_test_users):
    users = await create_test_users(2)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.post(
        "/api/chats/",
        params={"target_user_id": users[1]['id']}
    )

    assert response.status_code == 200

    data = response.json()

    async with session_factory() as session:
        query = or_(
            and_(ChatORM.user_1_id == users[0]['id'], ChatORM.user_2_id == users[1]['id']),
            and_(ChatORM.user_1_id == users[1]['id'], ChatORM.user_2_id == users[0]['id'])
        )

        existing_chat = await session.scalar(select(ChatORM).where(query))

    assert existing_chat is not None
    assert data['chat_id'] == existing_chat.id

# ================================ Get already existed chat ================================
@pytest.mark.asyncio
async def test_create_chat_exists(get_client, create_test_users, create_test_chat):
    users = await create_test_users(2)
    chat = await create_test_chat(users[0]['id'], users[1]['id'])

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.post(
        "/api/chats/",
        params={"target_user_id": users[1]['id']}
    )

    assert response.status_code == 200

    async with session_factory() as session:
        result = await session.scalars(select(ChatORM))
        chats = result.all()

    assert len(chats) == 1

    data = response.json()

    assert data['chat_id'] == chat['chat_id']
    
# ================================ Test create chat reverse users ================================
@pytest.mark.asyncio
async def test_create_chat_exists_reverse_orientation(get_client, create_test_users, create_test_chat):
    users = await create_test_users(2)
    chat = await create_test_chat(
        users[1]['id'],
        users[0]['id']
    )

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )
    assert login_response.status_code == 200

    response = await get_client.post(
        "/api/chats/",
        params={"target_user_id": users[1]['id']}
    )

    assert response.status_code == 200

    async with session_factory() as session:
        result = await session.scalars(select(ChatORM))
        chats = result.all()

    assert len(chats) == 1

    data = response.json()

    assert data['chat_id'] == chat['chat_id']

# ================================ Test create chat with yourself ================================
@pytest.mark.asyncio
async def test_create_chat_with_yourself(get_client, create_test_users):
    users = await create_test_users(1)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.post(
        "/api/chats/",
        params={"target_user_id": users[0]['id']}
    )

    assert response.status_code == 400

    data = response.json()

    assert data['detail']['error'] == "self_chat"
    assert data['detail']['message'] == "You cannot create a new chat with yourself"

# ================================ Test Target user does not exist ================================
@pytest.mark.asyncio
async def test_create_chat_target_user_not_exist(get_client, create_test_users):
    users = await create_test_users(1)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.post(
        "/api/chats/",
        params={"target_user_id": 999999}
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail']['error'] == "not_found"
    assert data['detail']['message'] == "User not found"

# ================================ Test not authorized ================================
@pytest.mark.asyncio
async def test_create_chat_not_authorized(get_client):
    response = await get_client.post(
        "/api/chats/",
        params={"target_user_id": 1}
    )

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "not_authenticated"
    assert data['detail']['message'] == "Not authenticated"

# ======================================================================
# ====================== GET CHAT HISTORY (GET) ========================
# ======================================================================

# ================================ Test get messages ================================
@pytest.mark.asyncio
async def test_get_chat_messages(get_client, create_test_users, create_test_chat, create_test_messages):
    users = await create_test_users(2)
    chat = await create_test_chat(users[0]['id'], users[1]['id'])

    user_0_messages = await create_test_messages(5, users[0]['id'], chat['chat_id'])
    user_1_messages = await create_test_messages(5, users[1]['id'], chat['chat_id'])

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(f"/api/chats/{chat['chat_id']}/messages")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 10

    expected_ids = {message['id'] for message in user_0_messages + user_1_messages}
    actual_ids = {message['message_id'] for message in data}

    assert expected_ids == actual_ids

# ================================ Test wrong existing chat ================================
@pytest.mark.asyncio
async def test_get_chat_messages_wrong_existing_chat(
    get_client,
    create_test_users,
    create_test_chat
):
    users = await create_test_users(4)
    chat_1 = await create_test_chat(users[0]['id'], users[1]['id'])
    chat_2 = await create_test_chat(users[2]['id'], users[3]['id'])

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(f"/api/chats/{chat_2['chat_id']}/messages")

    assert response.status_code == 404

    data = response.json()

    assert data['detail']['error'] == "not_found"
    assert data['detail']['message'] == "Chat not found"

# ================================ Chat does not exist ================================
@pytest.mark.asyncio
async def test_get_chat_messages_chat_not_exist(get_client, create_test_users):
    users = await create_test_users(1)

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(f"/api/chats/9999/messages")

    assert response.status_code == 404

    data = response.json()

    assert data['detail']['error'] == "not_found"
    assert data['detail']['message'] == "Chat not found"

# ================================ Test empty chat ================================
@pytest.mark.asyncio
async def test_get_empty_chat_messages(get_client, create_test_users, create_test_chat):
    users = await create_test_users(2)
    chat = await create_test_chat(users[0]['id'], users[1]['id'])

    login_response = await get_client.post(
        "/login/",
        json={
            "email": users[0]['email'],
            "password": users[0]['password']
        }
    )

    assert login_response.status_code == 200

    response = await get_client.get(f"/api/chats/{chat['chat_id']}/messages")

    assert response.status_code == 200

    data = response.json()

    assert data == []

# ================================ Test unauthorized user ================================
@pytest.mark.asyncio
async def test_get_chat_messages_unauthorized(get_client):
    response = await get_client.get("/api/chats/9999/messages")

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "not_authenticated"
    assert data['detail']['message'] == "Not authenticated"