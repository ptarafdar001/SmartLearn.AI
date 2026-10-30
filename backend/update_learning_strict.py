with open('backend/app/services/learning_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update get_enrolled_subjects: Strictly return only the subjects the student enrolled in
old_enrolled_fallback = """        # If student has no selections yet, fallback to all subjects for their board & grade
        if not canonical_subjects:
            if profile:
                canonical_subjects = LearningRepository.get_subjects_by_board_grade(
                    db,
                    board=profile.board,
                    grade=profile.grade,
                    academic_stream=profile.academic_stream,
                )
            else:
                canonical_subjects = LearningRepository.get_all_active_subjects(db)"""

new_enrolled_fallback = """        # If student has selections, ONLY return those exact subjects!
        # If student has zero selections recorded yet, return an empty list so we never bleed unselected default subjects
        if not selections:
            canonical_subjects = []"""

assert old_enrolled_fallback in code, "old_enrolled_fallback not found"
code = code.replace(old_enrolled_fallback, new_enrolled_fallback, 1)

# 2. Update get_continue_learning: Make sure the continued topic belongs strictly to one of the student's currently enrolled subjects!
old_continue = """        recent = recent_records[0]
        topic = LearningRepository.get_topic_by_id(db, recent.topic_id)
        if not topic:
            return None

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = LearningRepository.get_subject_by_id(db, chapter.subject_id) if chapter else None"""

new_continue = """        # Verify the topic belongs to the student's current enrolled subjects
        current_selections = OnboardingRepository.get_subject_selections(db, user_id)
        current_names = [s.subject_name.strip().lower() for s in current_selections]
        
        valid_record = None
        valid_topic = None
        valid_chapter = None
        valid_subject = None

        for rec in recent_records:
            t = LearningRepository.get_topic_by_id(db, rec.topic_id)
            if not t:
                continue
            ch = LearningRepository.get_chapter_by_id(db, t.chapter_id)
            if not ch:
                continue
            sub = LearningRepository.get_subject_by_id(db, ch.subject_id)
            if not sub:
                continue
            # Must match an active enrolled subject
            if current_names and sub.name.strip().lower() not in current_names:
                continue
            valid_record = rec
            valid_topic = t
            valid_chapter = ch
            valid_subject = sub
            break

        if not valid_record or not valid_topic:
            return None

        recent = valid_record
        topic = valid_topic
        chapter = valid_chapter
        subject = valid_subject"""

assert old_continue in code, "old_continue not found"
code = code.replace(old_continue, new_continue, 1)

with open('backend/app/services/learning_service.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated backend/app/services/learning_service.py successfully")

