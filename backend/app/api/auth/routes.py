from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register student account",
)
def register(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Register a new student account. Enforces unique email and password hashing."""
    try:
        return AuthService.register_user(db=db, data=data)
    except ValueError as e:
        err_msg = str(e)
        if "already registered" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=err_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive access token",
)
def login(data: UserLogin, db: Session = Depends(get_db)) -> Token:
    """
    Authenticate student credentials and return signed Bearer JWT token.
    Generic 401 error is returned for both invalid email or invalid password.
    """
    try:
        user = AuthService.authenticate_user(db=db, data=data)
        return AuthService.create_token_for_user(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Return profile data for the authenticated student. Passwords are never returned."""
    return UserResponse.model_validate(current_user)
