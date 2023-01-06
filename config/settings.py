import os
from pathlib import Path

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"

ENV_PATH = Path(__file__).parent.parent / '.env'

CONFIG = {
    'MONGODB_CONN_STRING': os.environ['MONGODB_CONN_STRING'],
    'DB': os.environ['DB']
}

JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']
