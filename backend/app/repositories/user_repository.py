from typing import Optional
from sqlalchemy.orm import Session

from app.models.users import User


class UserRepository:
    """Encapsulated persistence/data-access operations for the User entity."""

    @staticmethod
    def create(
        db: Session,
        email: str,
        hashed_password: str,
        full_name: str,
        role: str = "student",
        is_active: bool = True,
        is_onboarded: bool = False,
    ) -> User:
        """Persist a new User record in PostgreSQL."""
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            role=role.strip().lower(),
            is_active=is_active,
            is_onboarded=is_onboarded,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Fetch a User by primary key."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch a User by unique email (case-insensitive)."""
        return db.query(User).filter(User.email == email.strip().lower()).first()

    @staticmethod
    def update_onboarding_status(
        db: Session, user_id: int, is_onboarded: bool = True
    ) -> Optional[User]:
        """Update user onboarding completion flag."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_onboarded = is_onboarded
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Remove user entity and trigger cascading deletes."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
