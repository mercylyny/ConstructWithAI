import hashlib
import secrets
import json
import base64
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Secret key for JWT signing. In production, this should come from an environment variable.
SECRET_KEY = "build_ai_super_secret_signing_key_for_jwt_session_management_2026"
ALGORITHM = "HS256"
ITERATIONS = 600000

# Bearer token extractor
bearer_scheme = HTTPBearer(auto_error=False)

# --- Helper base64url encode/decode functions ---
def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

# --- PBKDF2 Password Hashing & Verification ---
def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 600,000 iterations.
    Returns: 'pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>'
    """
    salt = secrets.token_hex(16)
    hashed_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        ITERATIONS
    )
    hash_hex = hashed_bytes.hex()
    return f"pbkdf2_sha256${ITERATIONS}${salt}${hash_hex}"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its PBKDF2-HMAC-SHA256 hash in constant time.
    """
    try:
        parts = hashed_password.split('$')
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        
        iterations = int(parts[1])
        salt = parts[2]
        original_hash_hex = parts[3]
        
        new_hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        new_hash_hex = new_hash_bytes.hex()
        
        return secrets.compare_digest(original_hash_hex, new_hash_hex)
    except Exception:
        return False

# --- Lightweight JWT Signer (No External Dependencies) ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT token containing the data dictionary.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    
    payload = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=2)
    payload["exp"] = int(expire.timestamp())
    
    # Encode header and payload to json and base64url
    header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
    payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    
    header_b64 = base64url_encode(header_json)
    payload_b64 = base64url_encode(payload_json)
    
    # Signature calculation
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac_sign(signing_input, SECRET_KEY)
    signature_b64 = base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_access_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token. Returns payload dict or None if invalid.
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_signature = hmac_sign(signing_input, SECRET_KEY)
        actual_signature = base64url_decode(signature_b64)
        
        if not secrets.compare_digest(expected_signature, actual_signature):
            return None
            
        # Decode and parse payload
        payload_json = base64url_decode(payload_b64)
        payload = json.loads(payload_json.decode('utf-8'))
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or exp < time.time():
            return None
            
        return payload
    except Exception:
        return None

def hmac_sign(msg: bytes, key: str) -> bytes:
    import hmac
    return hmac.new(key.encode('utf-8'), msg, hashlib.sha256).digest()

# --- Password Reset Token Utility ---
def generate_reset_token() -> str:
    """
    Generate a cryptographically secure, URL-safe random reset token.
    """
    return secrets.token_urlsafe(32)

def generate_numeric_code(length: int = 6) -> str:
    """
    Generate a numeric code of the requested length suitable for SMS verification.
    """
    if length <= 0:
        length = 6
    # Ensure the first digit isn't zero by generating in range
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return str(secrets.randbelow(end - start + 1) + start)

# --- FastAPI Current User Dependency ---
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    """
    FastAPI dependency: reads the Bearer token, decodes it,
    and returns the user's email from the JWT payload.
    Returns None if no token is provided (so endpoints can be optional-auth).
    Raises 401 if the token is present but invalid/expired.
    """
    if credentials is None:
        return None  # No token – caller decides if this is allowed

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload.get("sub")  # Returns the user's email
