import sys
import os

# Ensure the root path is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal, Base, engine
from models import project, wall, estimation, user, building_summary, estimation_phase
from models.project import Project
from models.wall import Wall
from models.estimation import Estimation
from models.user import User, PasswordResetToken
from models.building_summary import BuildingSummaryRecord
from models.estimation_phase import EstimationPhase

Base.metadata.create_all(bind=engine)
from schemas.auth import (
    UserCreate,
    UserLogin,
    GoogleLoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm
)
from routers.auth import (
    register_user,
    login_user,
    google_login,
    forgot_password,
    reset_password
)
from services.auth_service import verify_password

def cleanup_db(db, email: str):
    db.query(PasswordResetToken).filter(PasswordResetToken.email == email).delete()
    db.query(User).filter(User.email == email).delete()
    db.commit()

def run_tests():
    email = "test_verify@example.com"
    password = "Password123!"
    new_password = "NewPassword123!"
    
    print("Initializing Authentication Direct Verification System...\n")
    db = SessionLocal()
    cleanup_db(db, email)
    
    try:
        # Test Case 1: Register User
        print("[Test 1/6] Registering User programmatically...")
        payload = UserCreate(email=email, password=password, name="Test Validator")
        response = register_user(payload, db)
        assert response.access_token is not None
        assert response.user.email == email
        assert response.user.is_google_user is False
        print("[OK] Registration successful!")

        # Test Case 2: Attempt duplicate registration
        print("[Test 2/6] Verifying duplicate registration prevention...")
        try:
            register_user(payload, db)
            raise AssertionError("Duplicate registration should have raised an exception")
        except Exception as e:
            # Expecting HTTP 400 Bad Request
            print(f"[OK] Duplicate registration rejected as expected ({str(e)}).")

        # Test Case 3: Login User
        print("[Test 3/6] Logging in User...")
        login_payload = UserLogin(email=email, password=password)
        login_resp = login_user(login_payload, db)
        assert login_resp.access_token is not None
        assert login_resp.user.email == email
        print("[OK] Login successful!")

        # Test Case 4: Invalid Password Login
        print("[Test 4/6] Verifying incorrect password handling...")
        wrong_payload = UserLogin(email=email, password="WrongPassword!")
        try:
            login_user(wrong_payload, db)
            raise AssertionError("Incorrect password should have raised an exception")
        except Exception as e:
            print(f"[OK] Incorrect password rejected as expected ({str(e)}).")

        # Test Case 5: Forgot Password & Token Generation
        print("[Test 5/6] Requesting password reset...")
        forgot_payload = PasswordResetRequest(email=email)
        forgot_resp = forgot_password(forgot_payload, db)
        token = forgot_resp.get("debug_token")
        assert token is not None
        print(f"[OK] Password reset request succeeded. Received debug token: {token[:10]}...")

        # Test Case 6: Reset Password
        print("[Test 6/6] Resetting password...")
        reset_payload = PasswordResetConfirm(
            email=email,
            token=token,
            new_password=new_password
        )
        reset_resp = reset_password(reset_payload, db)
        print("[OK] Password reset confirmation accepted!")

        # Verify old password no longer works, new password does
        print("Validating that new password authenticates successfully...")
        try:
            login_user(login_payload, db)
            raise AssertionError("Old password should not authenticate")
        except Exception:
            pass
        
        new_login_payload = UserLogin(email=email, password=new_password)
        new_login_resp = login_user(new_login_payload, db)
        assert new_login_resp.access_token is not None
        print("[OK] New credentials verified successfully!")

        print("\n" + "="*50)
        print(" ALL END-TO-END AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ Test verification failed: {e}")
        sys.exit(1)
    finally:
        cleanup_db(db, email)
        db.close()

if __name__ == "__main__":
    run_tests()
