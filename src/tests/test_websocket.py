import pytest
from messenger.utils.jwt.jwt import create_access_token
from fastapi import WebSocketDisconnect
from tests.conftest import session_factory
from sqlalchemy import select, or_, and_
from messenger.database.models import MessageORM
import random
import string


# ========================== Test successful websocket connection ==========================
@pytest.mark.asyncio
async def test_websocket_connection(websocket_client, create_test_user):
    token = create_access_token(create_test_user['user_id'])
    websocket_client.cookies.set("access_token", token)

    with websocket_client.websocket_connect("/chats/ws/") as websocket:
        pass

# ========================== Test Websocket connection token missing ==========================
@pytest.mark.asyncio
async def test_websocket_connection_wo_token(websocket_client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with websocket_client.websocket_connect("/chats/ws/") as websocket:
            pass

    assert exc.value.code == 1008

# ========================== Test Websocket connection wrong token ==========================
@pytest.mark.asyncio
async def test_websocket_wrong_access_token(websocket_client):
    websocket_client.cookies.set("access_token", "wrong_access_token")

    with pytest.raises(WebSocketDisconnect) as exc:
        with websocket_client.websocket_connect("/chats/ws/") as websocket:
            pass

    assert exc.value.code == 1008

# ========================== Test valid JWT but user not exists ==========================
@pytest.mark.asyncio
async def test_websocket_valid_jwt_not_user(websocket_client):
    token = create_access_token(999)
    websocket_client.cookies.set("access_token", token)

    with pytest.raises(WebSocketDisconnect) as exc:
        with websocket_client.websocket_connect("/chats/ws/") as websocket:
            pass

    assert exc.value.code == 1008

# ========================== Forbidden chat ==========================
@pytest.mark.asyncio
async def test_websocket_forbidden_chat(create_test_users, websocket_client, create_test_chat):
    users = await create_test_users(3)

    user_a = users[0]
    user_b = users[1]
    user_c = users[2]

    chat = await create_test_chat(user_b['id'], user_c['id'])

    token = create_access_token(user_a['id'])
    websocket_client.cookies.set("access_token", token)

    with websocket_client.websocket_connect("/chats/ws/") as websocket:
        websocket.send_json({
            "chat_id": chat['chat_id'],
            "content": "Hello!"
        })

        response = websocket.receive_json()

        assert response['error'] == "forbidden"
        assert response['message'] == "You are not a member of this chat"

# ========================== Test message is delivered ========================== 
@pytest.mark.asyncio
async def test_websocket_message_is_delivered(
    websocket_client,
    create_test_users,
    create_test_chat
):
    users = await create_test_users(2)

    user_a = users[0]
    user_b = users[1]

    chat = await create_test_chat(user_a["id"], user_b["id"])

    token_a = create_access_token(user_a["id"])
    token_b = create_access_token(user_b["id"])

    websocket_client.cookies.set("access_token", token_a)

    with websocket_client.websocket_connect("/chats/ws/") as websocket_a:
        websocket_client.cookies.set("access_token", token_b)

        with websocket_client.websocket_connect("/chats/ws/") as websocket_b:

            websocket_a.send_json({
                "chat_id": chat["chat_id"],
                "content": "hello"
            })

            response = websocket_b.receive_json()

            assert response["content"] == "hello"

# ========================== Test message is saved in DB ==========================
@pytest.mark.asyncio
async def test_websocket_message_is_saved(
    websocket_client,
    create_test_users,
    create_test_chat
):
    users = await create_test_users(2)
    user_a = users[0]
    user_b = users[1]

    chat = await create_test_chat(user_a['id'], user_b['id'])

    token_a = create_access_token(user_a['id'])
    token_b = create_access_token(user_b['id'])

    websocket_client.cookies.set("access_token", token_a)

    with websocket_client.websocket_connect("/chats/ws/") as websocket_a:
        websocket_client.cookies.set("access_token", token_b)

        with websocket_client.websocket_connect("/chats/ws/") as websocket_b:
            websocket_a.send_json({
                "chat_id": chat['chat_id'],
                "content": "hello"
            })

            websocket_b.receive_json()

    async with session_factory() as session:
        query = and_(
            MessageORM.chat_id == chat['chat_id'],
            MessageORM.sender_id == user_a['id'],
            MessageORM.content == "hello"
        )

        message_orm = await session.scalar(select(MessageORM).where(query))

        assert message_orm is not None

# ========================== Test Chat is None ==========================
@pytest.mark.asyncio
async def test_websocket_chat_is_none(create_test_users, websocket_client):
    users = await create_test_users(1)

    token = create_access_token(users[0]['id'])

    websocket_client.cookies.set("access_token", token)

    with websocket_client.websocket_connect("/chats/ws/") as websocket:
        websocket.send_json({
            "chat_id": 999999999,
            "content": "hello"
        })

        response = websocket.receive_json()

    assert response is not None
    assert response['error'] == "chat_not_found"

# ========================== Test invalid message ==========================
@pytest.mark.asyncio
async def test_websocket_invalid_message(create_test_users, websocket_client):
    users = await create_test_users(1)

    token = create_access_token(users[0]['id'])
    websocket_client.cookies.set("access_token", token)

    with websocket_client.websocket_connect("/chats/ws/") as websocket:
        websocket.send_json({
            "chat_id": 999999999,
            "content": "".join(random.choices(string.ascii_letters, k=513))
        })

        response = websocket.receive_json()

    assert response is not None
    assert response['error'] == "validate_error"
    assert response['message'] == "Invalid message"

# ========================== Test inverse communicating ==========================
@pytest.mark.asyncio
async def test_websocket_user_b_to_user_a(create_test_users, create_test_chat, websocket_client):
    users = await create_test_users(2)
    user_a = users[0]
    user_b = users[1]

    chat = await create_test_chat(user_a['id'], user_b['id'])

    websocket_client.cookies.set("access_token", create_access_token(user_a['id']))

    with websocket_client.websocket_connect("/chats/ws/") as websocket_a:
        websocket_client.cookies.set("access_token", create_access_token(user_b['id']))

        with websocket_client.websocket_connect("/chats/ws/") as websocket_b:
            websocket_b.send_json({
                "chat_id": chat['chat_id'],
                "content": "hello"
            })

            response = websocket_a.receive_json()


    assert response['chat_id'] == chat['chat_id']
    assert response['sender_id'] == user_b['id']

# ========================== Test recipient offline ==========================
@pytest.mark.asyncio
async def test_websocket_recipient_offline(create_test_users, create_test_chat, websocket_client):
    users = await create_test_users(2)
    user_a, user_b = users

    chat = await create_test_chat(user_a['id'], user_b['id'])

    websocket_client.cookies.set("access_token", create_access_token(user_a['id']))

    with websocket_client.websocket_connect("/chats/ws/") as websocket:
        websocket.send_json({
            "chat_id": chat['chat_id'],
            "content": "hello"
        })

        response = websocket.receive_json()

    assert response is not None
    assert response['type'] == "message_sent"

