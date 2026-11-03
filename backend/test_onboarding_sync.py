import sys
sys.path.insert(0, 'backend')
from app.db.session import SessionLocal
from app.models.users import User
from app.models.onboarding import StudentProfile, SubjectSelection, LearningPreference, StudyGoal, StudySchedule
from app.services.onboarding_service import OnboardingService
from app.services.learning_service import LearningService
from app.services.dashboard_service import DashboardService
from app.services.analytics_service import AnalyticsService
from app.schemas.onboarding import Step1BoardClass, Step2StreamSubjects, Step3PreferencesGoals, Step4Schedule

db = SessionLocal()
try:
    test_email = "sync.tester@smartlearn.ai"
    user = db.query(User).filter(User.email == test_email).first()
    if not user:
        from app.core.security import get_password_hash
        user = User(
            email=test_email,
            hashed_password=get_password_hash("Password@123"),
            full_name="Sync Test Student",
            role="student",
            is_active=True,
            is_onboarded=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    uid = user.id
    print(f"=== TEST RUN FOR USER {uid} ({test_email}) ===")

    # 1. First selection: History (Class 11 ISC)
    print("\n[STEP A] Saving Initial Onboarding: ISC Class 11 Humanities -> ['History']")
    OnboardingService.save_step1_board_class(db, uid, Step1BoardClass(board="ISC", grade="Class 11", academic_stream="Humanities / Arts"))
    OnboardingService.save_step2_stream_subjects(db, uid, Step2StreamSubjects(academic_stream="Humanities / Arts", subjects=["History"]))
    OnboardingService.save_step3_preferences_goals(db, uid, Step3PreferencesGoals(preferred_style="Reading & Notes", goals=["Score 90% in History"]))
    OnboardingService.save_step4_schedule(db, uid, Step4Schedule(daily_target_hours=2.0, preferred_slot="Evening", available_days=["Monday", "Wednesday", "Friday"]))

    # Verify unified selections
    selA = OnboardingService.get_current_selections(db, uid)
    subsA = LearningService.get_enrolled_subjects(db, uid)
    dashA = DashboardService.get_dashboard_overview(db, uid)
    recA = DashboardService.get_recommendations(db, uid)
    anaA = AnalyticsService.get_detailed_student_analytics(db, user)

    print(f" Unified Selections: Board={selA.board}, Grade={selA.grade}, Subjects={selA.enrolled_subjects}")
    print(f" Enrolled Subjects count={len(subsA)} -> {[s.name for s in subsA]}")
    print(f" Dashboard Overview: Board={dashA.board}, Grade={dashA.grade}, Subjects={dashA.enrolled_subjects}")
    print(f" Recommendations count={recA.total_count} -> {[r.subject for r in recA.recommendations[:2]]}")
    print(f" Analytics Chapters count={len(anaA.get('chapter_progress', []))} -> {[c['title'] for c in anaA.get('chapter_progress', [])[:2]]}")

    assert [s.name for s in subsA] == ["History"], f"Expected ['History'], got {[s.name for s in subsA]}"
    assert dashA.enrolled_subjects == ["History"], f"Expected ['History'], got {dashA.enrolled_subjects}"

    # 2. Student updates / switches onboarding to Sanskrit (CBSE Class 6)
    print("\n[STEP B] Student changes onboarding to: CBSE Class 6 -> ['Sanskrit']")
    OnboardingService.save_step1_board_class(db, uid, Step1BoardClass(board="CBSE", grade="Class 6"))
    OnboardingService.save_step2_stream_subjects(db, uid, Step2StreamSubjects(subjects=["Sanskrit"]))
    OnboardingService.save_step3_preferences_goals(db, uid, Step3PreferencesGoals(preferred_style="Visual Learner", goals=["Master Sanskrit Grammar"]))
    OnboardingService.save_step4_schedule(db, uid, Step4Schedule(daily_target_hours=1.5, preferred_slot="Morning", available_days=["Tuesday", "Thursday"]))

    # Verify unified selections again
    selB = OnboardingService.get_current_selections(db, uid)
    subsB = LearningService.get_enrolled_subjects(db, uid)
    dashB = DashboardService.get_dashboard_overview(db, uid)
    recB = DashboardService.get_recommendations(db, uid)
    anaB = AnalyticsService.get_detailed_student_analytics(db, user)

    print(f" Unified Selections: Board={selB.board}, Grade={selB.grade}, Subjects={selB.enrolled_subjects}")
    print(f" Enrolled Subjects count={len(subsB)} -> {[s.name for s in subsB]}")
    print(f" Dashboard Overview: Board={dashB.board}, Grade={dashB.grade}, Subjects={dashB.enrolled_subjects}")
    print(f" Recommendations count={recB.total_count} -> {[r.subject for r in recB.recommendations[:2]]}")
    print(f" Analytics Chapters count={len(anaB.get('chapter_progress', []))} -> {[c['title'] for c in anaB.get('chapter_progress', [])[:2]]}")

    # History MUST NOT appear anywhere!
    for s in subsB:
        assert "history" not in s.name.lower(), f"Stale subject found in enrolled subjects: {s.name}"
    for name in dashB.enrolled_subjects:
        assert "history" not in name.lower(), f"Stale subject found in dashboard overview: {name}"
    for r in recB.recommendations:
        assert "history" not in r.subject.lower(), f"Stale subject found in recommendations: {r.subject}"
    for c in anaB.get('chapter_progress', []):
        assert "history" not in c['title'].lower(), f"Stale subject found in analytics: {c['title']}"

    assert [s.name for s in subsB] == ["Sanskrit"], f"Expected ['Sanskrit'], got {[s.name for s in subsB]}"
    assert dashB.enrolled_subjects == ["Sanskrit"], f"Expected ['Sanskrit'], got {dashB.enrolled_subjects}"

    # 3. Student selects TWO subjects: Mathematics and Science (Class 10 CBSE)
    print("\n[STEP C] Student selects TWO subjects: CBSE Class 10 -> ['Mathematics', 'Science']")
    OnboardingService.save_step1_board_class(db, uid, Step1BoardClass(board="CBSE", grade="Class 10"))
    OnboardingService.save_step2_stream_subjects(db, uid, Step2StreamSubjects(subjects=["Mathematics", "Science"]))

    subsC = LearningService.get_enrolled_subjects(db, uid)
    dashC = DashboardService.get_dashboard_overview(db, uid)
    print(f" Enrolled Subjects count={len(subsC)} -> {[s.name for s in subsC]}")
    print(f" Dashboard Overview Subjects count={len(dashC.enrolled_subjects)} -> {dashC.enrolled_subjects}")
    assert set(s.name for s in subsC) == {"Mathematics", "Science"}
    assert set(dashC.enrolled_subjects) == {"Mathematics", "Science"}

    print("\n==========================================")
    print(">>> ALL ONBOARDING SYNC ASSERTIONS PASSED! <<<")
    print("==========================================")
finally:
    db.close()

