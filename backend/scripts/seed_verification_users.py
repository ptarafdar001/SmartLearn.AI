import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.users import User
from app.models.onboarding import (
    StudentProfile,
    SubjectSelection,
    LearningPreference,
    StudyGoal,
    StudySchedule,
)

def ensure_user(db: Session, email: str, name: str, board: str, grade: str, stream: str | None, subjects: list[str], goal: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash("Password@123"),
            full_name=name,
            role="student",
            is_active=True,
            is_onboarded=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.hashed_password = get_password_hash("Password@123")
        user.is_onboarded = True
        user.is_active = True
        db.commit()

    # Profile
    db.query(StudentProfile).filter(StudentProfile.user_id == user.id).delete()
    profile = StudentProfile(
        user_id=user.id,
        board=board,
        grade=grade,
        academic_stream=stream,
    )
    db.add(profile)

    # Subjects
    db.query(SubjectSelection).filter(SubjectSelection.user_id == user.id).delete()
    for s_name in subjects:
        db.add(SubjectSelection(user_id=user.id, subject_name=s_name))

    # Goal
    db.query(StudyGoal).filter(StudyGoal.user_id == user.id).delete()
    db.add(StudyGoal(user_id=user.id, goal_text=goal))

    # Preference
    db.query(LearningPreference).filter(LearningPreference.user_id == user.id).delete()
    db.add(LearningPreference(user_id=user.id, preferred_style="Visual"))

    # Schedule
    db.query(StudySchedule).filter(StudySchedule.user_id == user.id).delete()
    db.add(StudySchedule(user_id=user.id, daily_target_hours=2.0, preferred_slot="evening", available_days=["Monday", "Wednesday", "Friday"]))

    db.commit()
    print(f"Verified student setup: {email} -> {board} {grade} {subjects}")

def main():
    db = SessionLocal()
    try:
        # 1. ISC Class 11 History Student
        ensure_user(
            db=db,
            email="demo.student@smartlearn.ai",
            name="Ananya Sharma",
            board="ISC",
            grade="Class 11",
            stream="Humanities",
            subjects=["History"],
            goal="Score 95% in Board Exams"
        )

        # 2. CBSE Class 10 Science & In-Preparation Subject Student
        ensure_user(
            db=db,
            email="cbse.student@smartlearn.ai",
            name="Aarav Gupta",
            board="CBSE",
            grade="Class 10",
            stream=None,
            subjects=["Science", "Social Science"],
            goal="Master CBSE Science Board Curriculum"
        )

        # 3. Dedicated In-Preparation Subject Student
        ensure_user(
            db=db,
            email="prep.student@smartlearn.ai",
            name="Debanjan Roy",
            board="WBCHSE",
            grade="Class 12",
            stream="Science",
            subjects=["Physics"],
            goal="Prepare for State Higher Secondary Exams"
        )
    finally:
        db.close()

if __name__ == "__main__":
    main()
