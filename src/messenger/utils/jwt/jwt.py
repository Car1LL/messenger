from messenger.utils.jwt.jwt_config import jwt_settings
from datetime import datetime, timedelta, timezone
import jwt

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire
    }

    token = jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm="HS256")

    return token

def decode_access_token(token: str) -> int:
    result = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=["HS256"])

    if result.get("type") == "access":
        return int(result['sub'])
    else:
        raise ValueError("Token type should be access!")