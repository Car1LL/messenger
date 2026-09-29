from messenger.utils.jwt.jwt_config import jwt_settings
from datetime import datetime, timezone, timedelta
import jwt

def create_refresh_token(user_id: int) -> tuple[datetime, str]:
    expire = datetime.now(timezone.utc) + timedelta(days=2)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire
    }

    token = jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm="HS256")

    return expire, token

def decode_refresh_token(token: str) -> int:
    result = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=["HS256"])

    if result.get("type") == "refresh":
        return int(result['sub'])
    else:
        raise ValueError("Token type should be refresh!")