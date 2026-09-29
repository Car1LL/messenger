import hashlib

def get_hash_token(token: str) -> str:
    hash_token_bytes = hashlib.sha256(token.encode("utf-8"))

    return hash_token_bytes.hexdigest()

def verify_hash_token(hash_token: str, value: str) -> bool:
    value_token = get_hash_token(value)

    return True if value_token == hash_token else False