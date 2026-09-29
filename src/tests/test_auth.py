import pytest
from tests.conftest import session_factory
from sqlalchemy import select
from messenger.database.models import UserORM, RefreshSessionORM
from messenger.utils.password import verify_password
from messenger.utils.jwt.jwt import create_access_token, decode_access_token
from messenger.utils.jwt.refresh_token import create_refresh_token
from datetime import datetime, timezone, timedelta


# ====================================================================
# ======================== REGISTER ==================================
# ====================================================================

USERNAME = "alex"
EMAIL = "alex@example.com"
PASSWORD = "12345678Aa"

# ================================= Successful Registration =================================
@pytest.mark.asyncio
async def test_register_success(get_client):
    response = await get_client.post(
        "/register/",
        json={
            "username": USERNAME,
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    assert response.status_code == 200
    assert response.json() == {
            "message": "User registered successfully"
    }

    async with session_factory() as session:
        result = await session.execute(
        select(UserORM).where(UserORM.email == EMAIL)
    )
        user = result.scalar_one_or_none()

    assert user is not None
    assert user.username == USERNAME

# ================================= Duplicate Email =================================
@pytest.mark.asyncio
async def test_register_duplicate_email(get_client):
    async with session_factory() as session:
        user = UserORM(
            username="existing_user",
            email=EMAIL,
            hash_password="password"
        )

        session.add(user)
        await session.commit()

    response = await get_client.post(
        "/register/",
        json={
            "username": "new_user",
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    assert response.status_code == 409

    data = response.json()

    assert data['detail']['error'] == "email_exists"
    assert data['detail']['message'] == "Account with this email already exists"

# ================================= Invalid Email =================================
@pytest.mark.parametrize(
        "email",
        [
            "user@",
            "user.example",
            "@example.com",
            "email",
            "user @example.com",
            "user@example",
            ""
        ]
)
@pytest.mark.asyncio
async def test_register_invalid_email(get_client, email):
    response = await get_client.post(
        "/register/",
        json={
            "username": USERNAME,
            "password": PASSWORD,
            "email": email
        }
    )

    assert response.status_code == 422

# ================================= Invalid Password =================================
@pytest.mark.parametrize(
        "password",
        [   
            "",
            "12345678", # no letters
            "12345678A", # no lowercase
            "12345678a", # no uppercase
            "123Aa", # too short
            "12345678912345678912345678900ABC00abc", # too long
            "StrongPassword" # no digits
        ]
)
@pytest.mark.asyncio
async def test_register_invalid_password(get_client, password):
    response = await get_client.post(
        "/register/",
        json={
            "username": USERNAME,
            "email": EMAIL,
            "password": password
        }
    )

    assert response.status_code == 422

# ================================= Save Hash Password =================================
@pytest.mark.asyncio
async def test_register_hash_password(get_client):
    response = await get_client.post(
        "/register/",
        json={
            "username": USERNAME,
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    assert response.status_code == 200

    async with session_factory() as session:
        result = await session.execute(select(UserORM).where(UserORM.email == EMAIL))
        user = result.scalar_one_or_none()

    assert user is not None
    assert user.hash_password != PASSWORD
    assert verify_password(PASSWORD, user.hash_password)

# ================================= Hash Passwords have Salt =================================
@pytest.mark.asyncio
async def test_register_same_password_produces_different_hash(get_client):
    user1_email = "user1@example.com"
    user2_email = "user2@example.com"
    username1 = "alex"
    username2 = "alex2"

    response_1 = await get_client.post(
        "/register/",
        json={
            "username": username1,
            "email": user1_email,
            "password": PASSWORD
        }
    )

    response_2 = await get_client.post(
        "/register/",
        json={
            "username": username2,
            "email": user2_email,
            "password": PASSWORD
        }
    )

    assert response_1.status_code == 200
    assert response_2.status_code == 200

    async with session_factory() as session:
        result_1 = await session.execute(select(UserORM).where(UserORM.email == user1_email))
        result_2 = await session.execute(select(UserORM).where(UserORM.email == user2_email))

        user1 = result_1.scalar_one_or_none()
        user2 = result_2.scalar_one_or_none()

    assert user1 is not None
    assert user2 is not None

    assert user1.hash_password != PASSWORD
    assert user2.hash_password != PASSWORD

    assert verify_password(PASSWORD, user1.hash_password)
    assert verify_password(PASSWORD, user2.hash_password)

    assert user1.hash_password != user2.hash_password

# ================================= Invalid Username =================================
@pytest.mark.parametrize(
        "username",
        [   
            "",
            "ab", # too short
            "SuperLongUsernameOverTwentyCharactersInIt", # too long
            "alex bob", # has whitespace
            "alex@bob", # incorrect characters
            "alex#", # incorrect characters
            "alex=+-" # incorrect characters
        ]
)
@pytest.mark.asyncio
async def test_register_invalid_username(get_client, username):
    response = await get_client.post(
        "/register/",
        json={
            "email": EMAIL,
            "password": PASSWORD,
            "username": username
        }
    )

    assert response.status_code == 422

# ================================= Username Duplicate =================================
@pytest.mark.asyncio
async def test_register_username_duplicate(get_client):
    username = "alex"
    
    response = await get_client.post(
        "/register/",
        json={
            "username": username,
            "email": "alex12@gmail.com",
            "password": PASSWORD
        }
    )

    assert response.status_code == 200

    response_2 = await get_client.post(
        "/register/",
        json={
            "username": username,
            "email": "alex21@gmail.com",
            "password": PASSWORD
        }
    )

    assert response_2.status_code == 409

    data = response_2.json()

    assert data['detail']['error'] == "username_exists"
    assert data['detail']['message'] == "This username is already taken"

# ================================= Register Missing =================================
@pytest.mark.parametrize(
        "json_input",
        [
            {
                "email": EMAIL,
                "password": PASSWORD
            },
            {
                "username": USERNAME,
                "password": PASSWORD
            },
            {
                "email": EMAIL,
                "username": USERNAME
            }
        ]
)
@pytest.mark.asyncio
async def test_register_missing_required_field(get_client, json_input):
    response = await get_client.post(
        "/register/",
        json=json_input
    )

    assert response.status_code == 422

    data = response.json()["detail"][0]

    assert data['type'] == "missing"
    assert data['msg'] == "Field required"

# =============================================================================
# ======================== CHECK USERNAME =====================================
# =============================================================================

# ================================= Username is available =================================
@pytest.mark.asyncio
async def test_check_username_available(get_client):
    response = await get_client.get(
        "/check-username/",
        params={"username": "alex"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "available": True,
        "message": "Username is available"
    }

# ================================= Username is taken =================================
@pytest.mark.asyncio
async def test_check_username_is_taken(get_client):
    username = "alex"

    response = await get_client.post(
        "/register/",
        json={
            "username": username,
            "email": "alex12@gmail.com",
            "password": PASSWORD
        }
    )

    assert response.status_code == 200

    response_2 = await get_client.get(
        "/check-username/",
        params={"username": username}
    )

    assert response_2.json() == {
        "available": False,
        "message": "This username is already taken"
    }

# ================================= Valid username =================================
@pytest.mark.parametrize(
        "username",
        [
            "abc",
            "abcdefg",
            "123abc",
            "abc123",
            "a1b1c1",
            "_a_b_c",
            "_123_ab_c"
        ]
)
@pytest.mark.asyncio
async def test_valid_username(get_client, username):
    response = await get_client.post(
        "/register/",
        json={
            "username": username,
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    assert response.status_code == 200

# ================================= Invalid username =================================
@pytest.mark.parametrize(
        "username",
        [
            "ab",
            "a1b",
            "12_a",
            "123456",
            "a_b_1",
            "1a2b_3"
        ]
)
@pytest.mark.asyncio
async def test_invalid_username(get_client, username):
    response = await get_client.post(
        "/register/",
        json={
            "username": username,
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    assert response.status_code == 422

# ====================================================================
# ======================== LOGIN =====================================
# ====================================================================

# ================================= Successful Login =================================
@pytest.mark.asyncio
async def test_login_success(get_client, create_test_user):
    response = await get_client.post(
        "/login/",
        json={
            "email": create_test_user['email'],
            "password": create_test_user['password']
        }
    )

    assert response.status_code == 200

# ================================= Login Invalid Password =================================
@pytest.mark.asyncio
async def test_login_invalid_password(get_client, create_test_user):
    response = await get_client.post(
        "/login/",
        json={
            "email": create_test_user['email'],
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "invalid_credentials"
    assert data['detail']['message'] == "Invalid email or password"

# ================================= Login Invalid Email =================================
@pytest.mark.asyncio
async def test_login_invalid_email(get_client):
    response = await get_client.post(
        "/login/",
        json={
            "email": "fakemail@gmail.com",
            "password": "SuperPassword"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "invalid_credentials"
    assert data['detail']['message'] == "Invalid email or password"

# ================================= Login Missing =================================
@pytest.mark.parametrize(
        "json_input",
        [
            {
                "email": "email@gmail.com"
            },
            {
                "password": "12345678Aa"
            }
        ]
)
@pytest.mark.asyncio
async def test_login_missing_required_fields(get_client, json_input):
    response = await get_client.post(
        "/login/",
        json=json_input
    )

    assert response.status_code == 422

    data = response.json()['detail'][0]

    assert data['type'] == "missing"
    assert data['msg'] == "Field required"

# ====================================================================
# ======================== TEST HOME PAGE ============================
# ======================== TEST REDIRECTION ==========================
# ====================================================================

# ================================= Test home without auth =================================
@pytest.mark.asyncio
async def test_home_without_auth(get_client):
    response = await get_client.get("/")

    assert response.status_code == 302
    assert response.headers["location"] == "/welcome/"

# ================================= Test home with auth =================================
@pytest.mark.asyncio
async def test_home_with_auth(get_client, create_test_user):
    token = create_access_token(create_test_user['user_id'])
    get_client.cookies.set("access_token", token)

    response = await get_client.get("/")

    assert response.status_code == 302
    assert response.headers["location"] == "/chats/"

# ================================= Test home with invalid auth =================================
@pytest.mark.asyncio
async def test_home_with_invalid_auth(get_client):
    get_client.cookies.set("access_token", "invalid-token")

    response = await get_client.get("/")

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "invalid_token"
    assert data['detail']['message'] == "Invalid or expired token"

# ====================================================================
# ====================== TEST REFRESH TOKEN ==========================
# ====================================================================

# ================================== Login success ==================================
@pytest.mark.asyncio
async def test_success_refresh_token(get_client, create_test_user):
    # Login
    login_response = await get_client.post(
        "/login/",
        json={
            "email": create_test_user['email'],
            "password": create_test_user['password']
        }
    )

    assert login_response.status_code == 200

    # Get refresh token
    refresh_token = get_client.cookies.get("refresh_token")

    assert refresh_token is not None

    # Refresh access token
    response = await get_client.post("/auth/refresh/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Token created successfully"
    }

    # Check new token was created
    access_token = get_client.cookies.get("access_token")

    assert access_token is not None

    user_id = decode_access_token(access_token)

    assert user_id == create_test_user['user_id']

# ================================== Refresh without token ==================================
@pytest.mark.asyncio
async def test_without_token(get_client):
    response = await get_client.post("/auth/refresh/")

    assert response.status_code == 401
    assert response.json()['detail']['error'] == "missing_refresh_token"

# ================================== Test Invalid Refresh Token ==================================
@pytest.mark.asyncio
async def test_refresh_invalid_token(get_client):
    get_client.cookies.set("refresh_token", "invalid_token")

    response = await get_client.post("/auth/refresh/")

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "invalid_refresh_token"

# ================================== Test Missing Refresh Session ==================================
@pytest.mark.asyncio
async def test_missing_refresh_session(get_client, create_test_user):
    _, refresh_token = create_refresh_token(create_test_user['user_id'])

    get_client.cookies.set("refresh_token", refresh_token)

    response = await get_client.post("/auth/refresh/")

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "refresh_session_not_found"

# ================================== Test Refresh Session revoked ==================================
@pytest.mark.asyncio
async def test_refresh_session_revoked(get_client, create_test_user):
    login_response = await get_client.post(
        "/login/",
        json={
            "email": create_test_user['email'],
            "password": create_test_user['password']
        }
    )

    assert login_response.status_code == 200

    async with session_factory() as session:
        refresh_token = await session.scalar(select(RefreshSessionORM).where(
            RefreshSessionORM.user_id == create_test_user['user_id']
        ))

        refresh_token.revoked_at = datetime.now(timezone.utc)
        await session.commit()

    response = await get_client.post("/auth/refresh/")

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "refresh_session_revoked"

# ================================== Test Refresh Session Expired ==================================
@pytest.mark.asyncio
async def test_refresh_session_expired(get_client, create_test_user):
    login_response = await get_client.post(
        "/login/",
        json={
            "email": create_test_user['email'],
            "password": create_test_user['password']
        }
    )

    assert login_response.status_code == 200

    async with session_factory() as session:
        refresh_session = await session.scalar(select(RefreshSessionORM).where(
            RefreshSessionORM.user_id == create_test_user['user_id']
        ))

        refresh_session.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        await session.commit()

    response = await get_client.post("/auth/refresh/")

    assert response.status_code == 401

    data = response.json()

    assert data['detail']['error'] == "refresh_session_expired"