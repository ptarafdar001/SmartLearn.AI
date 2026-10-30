with open('backend/app/services/analytics_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace chapter_progress_list resolution to only look up subjects strictly enrolled in subject_selections for the student's board/grade
old_ch_prog = """        # 5. Real Chapter Progress from enrolled subjects
        chapter_progress_list = []
        if selections:
            subject_names = [s.subject_name for s in selections]
            subjects = db.query(Subject).filter(Subject.name.in_(subject_names)).all()
            for s in subjects:
                for ch in s.chapters[:3]:
                    topic_ids = [t.id for t in ch.topics]
                    ch_progress_recs = [p for p in progress_records if p.topic_id in topic_ids]
                    if ch_progress_recs:
                        ch_pct = int(sum(p.progress_percentage or 0 for p in ch_progress_recs) / len(ch_progress_recs))
                    else:
                        attempts_count = 0
                        for a in attempts:
                            if a.practice_question_id:
                                pq = db.query(PracticeQuestion).filter(PracticeQuestion.id == a.practice_question_id).first()
                                if pq and pq.topic_id in topic_ids:
                                    attempts_count += 1
                        ch_pct = min(100, attempts_count * 25)
                    
                    color = "#10b981" if ch_pct >= 80 else "#f59e0b" if ch_pct >= 40 else "#6366f1"
                    chapter_progress_list.append({
                        "title": f"Ch {ch.chapter_number} · {ch.title}",
                        "progress": ch_pct,
                        "color": color,
                    })

        if not chapter_progress_list:
            default_chapters = db.query(Chapter).order_by(Chapter.id).limit(3).all()
            for ch in default_chapters:
                chapter_progress_list.append({
                    "title": f"Ch {ch.chapter_number} · {ch.title}",
                    "progress": 0,
                    "color": "#6366f1",
                })"""

new_ch_prog = """        # 5. Real Chapter Progress derived STRICTLY from student's enrolled subjects
        chapter_progress_list = []
        if selections:
            subject_names = [s.subject_name.strip() for s in selections]
            # Match canonical subjects for this student's board, grade, and enrolled names
            board = profile.board if profile else None
            grade = profile.grade if profile else None
            
            from app.services.learning_service import LearningService
            user_canonical_subjects = []
            for s_name in subject_names:
                canonical = LearningService._ensure_canonical_subject_for_selection(db, user_id=user_id, subject_name=s_name)
                if canonical and canonical not in user_canonical_subjects:
                    user_canonical_subjects.append(canonical)
                    
            for s in user_canonical_subjects:
                for ch in s.chapters[:2]:
                    topic_ids = [t.id for t in ch.topics]
                    ch_progress_recs = [p for p in progress_records if p.topic_id in topic_ids]
                    if ch_progress_recs:
                        ch_pct = int(sum(p.progress_percentage or 0 for p in ch_progress_recs) / len(ch_progress_recs))
                    else:
                        attempts_count = 0
                        for a in attempts:
                            if a.practice_question_id:
                                pq = db.query(PracticeQuestion).filter(PracticeQuestion.id == a.practice_question_id).first()
                                if pq and pq.topic_id in topic_ids:
                                    attempts_count += 1
                        ch_pct = min(100, attempts_count * 25)
                    
                    color = "#10b981" if ch_pct >= 80 else "#f59e0b" if ch_pct >= 40 else "#6366f1"
                    chapter_progress_list.append({
                        "title": f"{s.name}: Ch {ch.chapter_number} · {ch.title}",
                        "progress": ch_pct,
                        "color": color,
                    })"""

assert old_ch_prog in code, "old_ch_prog not found"
code = code.replace(old_ch_prog, new_ch_prog, 1)

with open('backend/app/services/analytics_service.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated backend/app/services/analytics_service.py successfully")

