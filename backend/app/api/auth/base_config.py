from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from app import User
from app.api.auth.manager import get_user_manager
from app.api.auth.user_db import get_jwt_strategy


bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
