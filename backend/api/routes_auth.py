"""API Routes for User Registration and JWT Login."""

from fastapi import APIRouter, HTTPException, status
from backend.schemas.api_schemas import UserLoginRequest, UserRegisterRequest, TokenResponse
from backend.authentication.auth_handler import AuthHandler

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user store for standalone execution
USER_STORE = {
    "admin": {
        "password": AuthHandler.hash_password("admin123"),
        "role": "admin",
        "email": "admin@cryptotrace.ai"
    },
    "analyst": {
        "password": AuthHandler.hash_password("analyst123"),
        "role": "investigator",
        "email": "analyst@cryptotrace.ai"
    }
}


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegisterRequest):
    if payload.username in USER_STORE:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = AuthHandler.hash_password(payload.password)
    USER_STORE[payload.username] = {
        "password": hashed,
        "role": payload.role or "investigator",
        "email": payload.email
    }

    token = AuthHandler.create_access_token({"sub": payload.username, "role": payload.role or "investigator"})
    return TokenResponse(access_token=token, role=payload.role or "investigator", username=payload.username)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    user = USER_STORE.get(payload.username)
    if not user or not AuthHandler.verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = AuthHandler.create_access_token({"sub": payload.username, "role": user["role"]})
    return TokenResponse(access_token=token, role=user["role"], username=payload.username)
