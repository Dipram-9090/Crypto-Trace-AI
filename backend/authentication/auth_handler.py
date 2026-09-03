"""Authentication Handler: JWT Token Creation, Verification, and RBAC Guards."""

import os
import time
import hmac
import hashlib
import base64
import json
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("cryptotrace.backend.auth")

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-crypto-trace-jwt-key-32-chars-long")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600 * 24

security_bearer = HTTPBearer(auto_error=False)


class AuthHandler:
    """Provides pure-python HMAC-SHA256 JWT tokens and PBKDF2 password hashing."""

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return f"{base64.b64encode(salt).decode('ascii')}${base64.b64encode(key).decode('ascii')}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            salt_b64, key_b64 = hashed_password.split("$")
            salt = base64.b64decode(salt_b64.encode("ascii"))
            expected_key = base64.b64decode(key_b64.encode("ascii"))
            computed_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000)
            return hmac.compare_digest(expected_key, computed_key)
        except Exception:
            return False

    @staticmethod
    def create_access_token(payload: Dict[str, Any], expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        exp = int(time.time()) + expires_delta
        token_payload = {**payload, "exp": exp}

        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(token_payload).encode()).decode().rstrip("=")

        signature = hmac.new(
            SECRET_KEY.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{header_b64}.{payload_b64}.{sig_b64}"

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            header_b64, payload_b64, sig_b64 = parts
            sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))

            expected_sig = hmac.new(
                SECRET_KEY.encode(),
                f"{header_b64}.{payload_b64}".encode(),
                hashlib.sha256
            ).digest()

            if not hmac.compare_digest(sig, expected_sig):
                raise ValueError("Signature mismatch")

            payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)).decode()
            payload = json.loads(payload_json)

            if payload.get("exp", 0) < int(time.time()):
                raise ValueError("Token expired")

            return payload
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired credentials: {e}"
            )


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Dict[str, Any]:
    """FastAPI Dependency for token extraction and authentication."""
    if not credentials:
        # Allow development guest if not configured
        return {"username": "analyst_guest", "role": "investigator"}
    return AuthHandler.decode_token(credentials.credentials)


def require_role(required_role: str):
    """RBAC Guard decorator/dependency."""
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        if user.get("role") != required_role and user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires role: {required_role}"
            )
        return user
    return role_checker
