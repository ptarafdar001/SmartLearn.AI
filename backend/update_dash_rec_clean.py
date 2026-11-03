with open('backend/app/services/dashboard_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace get_recommendations to ensure canonical matching uses _ensure_canonical_subject_for_selection
old_rec_block = """        # Map each enrolled subject to canonical learning resources (videos and key topics)
        for s in subjects:
            canonical = None
            if board and grade:
                candidate_subjects = LearningRepository.get_subjects_by_board_grade(
                    db, board=board, grade=grade, academic_stream=profile.academic_stream if profile else None
                )
                for cand in candidate_subjects:
                    if cand.name.lower() == s.subject_name.lower():
                        canonical = cand
                        break"""

new_rec_block = """        # Map each enrolled subject strictly to its canonical subject using single source of truth
        from app.services.learning_service import LearningService
        for s in subjects:
            canonical = LearningService._ensure_canonical_subject_for_selection(
                db, user_id=user_id, subject_name=s.subject_name
            )"""

assert old_rec_block in code, "old_rec_block not found"
code = code.replace(old_rec_block, new_rec_block, 1)

with open('backend/app/services/dashboard_service.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated backend/app/services/dashboard_service.py successfully")

