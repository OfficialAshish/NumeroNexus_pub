# jwt.py

import datetime
from jose import JWTError, jwt
from .config import JWT_KEY

SECRET_KEY = JWT_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30 * 5  # 5 months

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=150)  # 5 months
    to_encode.update({"exp": expiration.timestamp()})  # Ensure it's a timestamp
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
