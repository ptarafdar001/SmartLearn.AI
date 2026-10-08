"""
Seed script to create or reset the verified demo student account for SmartLearn.AI.
User: demo.student@smartlearn.ai
Password: Password@123
"""

import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models import (
    User,
    StudentProfile,
    SubjectSelection,
    LearningPreference,
    StudyGoal,
    StudySchedule,
    Subject,
)

def seed_demo_student(db: Session):
    email = "demo.student@smartlearn.ai"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash("Password@123"),
            full_name="Demo Student",
            is_active=True,
            is_onboarded=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created demo user: {user.email} (id={user.id})")
    else:
        user.is_onboarded = True
        user.hashed_password = get_password_hash("Password@123")
        db.commit()
        print(f"Updated demo user: {user.email} (id={user.id})")

    # Profile
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=user.id,
            board="ISC",
            grade="Class 11",
            stream="Humanities / Arts"
        )
        db.add(profile)
    else:
        profile.board = "ISC"
        profile.grade = "Class 11"
        profile.stream = "Humanities / Arts"

    # Subject Selection
    hist_subj = db.query(Subject).filter(Subject.code == "isc-11-hist").first()
    subj_id = hist_subj.id if hist_subj else 1
    
    existing_subjs = db.query(SubjectSelection).filter(SubjectSelection.user_id == user.id).all()
    if not existing_subjs:
        selection = SubjectSelection(
            user_id=user.id,
            subject_id=subj_id,
            is_primary=True
        )
        db.add(selection)

    # Preferences
    pref = db.query(LearningPreference).filter(LearningPreference.user_id == user.id).first()
    if not pref:
        pref = LearningPreference(
            user_id=user.id,
            preferred_pace="moderate",
            learning_style="visual_and_conceptual",
            explanation_depth="detailed"
        )
        db.add(pref)

    # Goals
    goal = db.query(StudyGoal).filter(StudyGoal.user_id == user.id).first()
    if not goal:
        goal = StudyGoal(
            user_id=user.id,
            primary_goal="Excel in Board Exams",
            target_percentage=95.0
        )
        db.add(goal)

    # Schedule
    sched = db.query(StudySchedule).filter(StudySchedule.user_id == user.id).first()
    if not sched:
        sched = StudySchedule(
            user_id=user.id,
            daily_study_hours=2.0,
            preferred_time_of_day="evening",
            days_per_week=6
        )
        db.add(sched)

    db.commit()
    print("Demo student onboarding data seeded successfully!")

if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed_demo_student(session)
    finally:
        session.close()
