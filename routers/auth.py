from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import secrets

from database.db import get_db
from models.user import User, PasswordResetToken
from schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    GoogleLoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    TokenResponse
)
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    generate_reset_token,
    generate_numeric_code
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication Operations"]
)

@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please login instead."
        )
    
    # 2. Create user with hashed password
    hashed = hash_password(payload.password)
    new_user = User(
        email=payload.email.lower(),
        hashed_password=hashed,
        name=payload.name,
        is_google_user=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 3. Create access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    # 1. Find user by email
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email. Please sign up first."
        )
    
    # 2. Check if user is a Google-only account without password
    if user.is_google_user and not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is registered via Google Sign-In. Please sign in with Google."
        )

    # 3. Verify password
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again."
        )
    
    # 4. Create token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/google-login", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    
    # 2. If not, auto-register the account
    if not user:
        # Create a randomized safe password string that is hashed, 
        # so traditional login doesn't work until they explicitly reset password
        random_pw = secrets.token_urlsafe(24) + "GoogleOAuthUser123!"
        hashed = hash_password(random_pw)
        user = User(
            email=payload.email.lower(),
            hashed_password=hashed,
            name=payload.name,
            is_google_user=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    # 3. Create token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/forgot-password")
def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    
    # Secure Practice: Even if user does not exist, return success to prevent user enumeration
    # But only perform sending / printing logic if the user does exist.
    debug_token = None
    if user:
        # 2. Invalidate previous tokens
        db.query(PasswordResetToken).filter(
            PasswordResetToken.email == user.email,
            PasswordResetToken.used == False
        ).update({PasswordResetToken.used: True})

        # 3. Choose delivery method: email (default) or sms
        if payload.via.lower() == "sms" and payload.phone:
            # Use a short numeric code for SMS
            code = generate_numeric_code()
            token = code
            debug_token = token
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

            db_token = PasswordResetToken(
                email=user.email,
                token=token,
                expires_at=expires_at,
                used=False
            )
            db.add(db_token)
            db.commit()

            # Simulated SMS output
            print("\n" + "="*80)
            print(" [SIMULATED SMS - OUTBOUND PASSWORD RESET CODE]")
            print(f" To (phone): {payload.phone}")
            print(f" Message: Your ConstructAI password reset code is {code}")
            print("="*80 + "\n")
        else:
            # Default: email delivery using a secure URL token
            token = generate_reset_token()
            debug_token = token
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            db_token = PasswordResetToken(
                email=user.email,
                token=token,
                expires_at=expires_at,
                used=False
            )
            db.add(db_token)
            db.commit()

            # Generate the reset link
            reset_link = f"http://localhost:3000/?view=reset-password&token={token}&email={user.email}"

            # Output link to stdout for simulated SMTP console
            print("\n" + "="*80)
            print(" [SIMULATED SMTP SERVER - OUTBOUND PASSWORD RESET EMAIL]")
            print(f" To: {user.email}")
            print(" Subject: Reset your ConstructAI Password")
            print(f" Secure Reset Link: {reset_link}")
            print("="*80 + "\n")

    return {
        "message": "If an account matches this email, a secure password reset link or code has been sent.",
        "debug_token": debug_token
    }

@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    # 1. Find active reset token
    db_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.email == payload.email.lower(),
        PasswordResetToken.token == payload.token,
        PasswordResetToken.used == False
    ).first()
    
    # 2. Validate token presence, use, and expiration
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset link is invalid or has already been used."
        )
        
    now = datetime.now(timezone.utc)
    # Ensure expires_at has timezone information for comparison
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
        
    if expires_at < now:
        db_token.used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset link has expired."
        )
        
    # 3. Find user
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to reset password. Email session has expired."
        )
        
    # 4. Update user password and disable Google-only lock
    user.hashed_password = hash_password(payload.new_password)
    user.is_google_user = False # Now they have a password and can log in normally
    
    # 5. Mark token as used
    db_token.used = True
    db.commit()
    
    return {"message": "Your password has been reset successfully!"}
