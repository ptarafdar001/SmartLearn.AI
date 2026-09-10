from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse


class AuthService:
    """Business logic service for user registration, authentication, and token management."""

    @staticmethod
    def register_user(db: Session, data: UserCreate) -> UserResponse:
        """
        Register a new student account.
        Validates duplicate email, hashes password, and persists user record via UserRepository.
        """
        existing_user = UserRepository.get_by_email(db, data.email)
        if existing_user:
            raise ValueError("Email is already registered")

        hashed_password = get_password_hash(data.password)

        user = UserRepository.create(
            db=db,
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
            role=data.role,
            is_active=True,
            is_onboarded=False,
        )
        return UserResponse.model_validate(user)

    @staticmethod
    def authenticate_user(db: Session, data: UserLogin) -> User:
        """
        Verify credentials and return authenticated User entity.
        Raises ValueError if credentials are invalid or user is inactive.
        """
        user = UserRepository.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Inactive user account")

        return user

    @staticmethod
    def create_token_for_user(user: User) -> Token:
        """Generate a signed JWT access token for an authenticated user."""
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"role": user.role, "email": user.email},
        )
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> UserResponse:
        """Retrieve user profile by ID."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        return UserResponse.model_validate(user)
