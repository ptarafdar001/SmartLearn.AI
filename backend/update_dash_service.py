import re

with open('backend/app/services/dashboard_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect get_recommendations
old_func = '''    @staticmethod
    def get_recommendations(db: Session, user_id: int) -> RecommendationsResponse:
        """
        Generate deterministic study recommendations directly based on the user's
        enrolled subjects, grade, board, and learning preference.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        pref = OnboardingRepository.get_learning_preference(db, user_id)
        goals = OnboardingRepository.get_study_goals(db, user_id)

        recommendations: List[RecommendationItem] = []

        style = pref.preferred_style if pref else "Interactive"
        board = profile.board if profile else "Curriculum"
        grade = profile.grade if profile else "Current Level"

        # Generate subject starter recommendations
        for s in subjects:
            rec_id = f"rec-subj-{s.id}"
            title = f"{s.subject_name}: Foundation & Concept Mapping"
            description = (
                f"Begin your {grade} ({board}) studies in {s.subject_name} using "
                f"{style.lower()} study techniques."
            )
            recommendations.append(
                RecommendationItem(
                    id=rec_id,
                    title=title,
                    description=description,
                    subject=s.subject_name,
                    learning_style=pref.preferred_style if pref else None,
                    recommendation_type="starter_guide",
                )
            )

        # Generate goal-oriented recommendations
        for g in goals:
            rec_id = f"rec-goal-{g.id}"
            exam_info = f" for {g.target_exam}" if g.target_exam else ""
            title = f"Goal Plan: {g.goal_text}"
            description = f"Structure your study sessions towards target: {g.goal_text}{exam_info}."
            recommendations.append(
                RecommendationItem(
                    id=rec_id,
                    title=title,
                    description=description,
                    subject="General Preparation",
                    learning_style=pref.preferred_style if pref else None,
                    recommendation_type="goal_milestone",
                )
            )

        return RecommendationsResponse(
            user_id=user.id,
            recommendations=recommendations,
            total_count=len(recommendations),
        )'''

new_func = '''    @staticmethod
    def get_recommendations(db: Session, user_id: int) -> RecommendationsResponse:
        """
        Generate curriculum-grounded video recommendations and study modules directly based
        on the student's enrolled subjects, grade, board, and topics.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        pref = OnboardingRepository.get_learning_preference(db, user_id)

        recommendations: List[RecommendationItem] = []
        style = pref.preferred_style if pref else "Interactive"
        board = profile.board if profile else "Curriculum"
        grade = profile.grade if profile else "Current Level"

        # Map each enrolled subject to canonical learning resources (videos and key topics)
        for s in subjects:
            canonical = None
            if board and grade:
                candidate_subjects = LearningRepository.get_subjects_by_board_grade(
                    db, board=board, grade=grade, academic_stream=profile.academic_stream if profile else None
                )
                for cand in candidate_subjects:
                    if cand.name.lower() == s.subject_name.lower():
                        canonical = cand
                        break

            if canonical:
                chapters = LearningRepository.get_chapters_by_subject_id(db, canonical.id)
                for ch in chapters:
                    topics = LearningRepository.get_topics_by_chapter_id(db, ch.id)
                    for top in topics:
                        resources = LearningRepository.get_resources_by_topic_id(db, top.id, only_active=True)
                        video_res = next((r for r in resources if r.resource_type == "video"), None)
                        
                        vid_id = video_res.external_id if video_res else "kYJq1000m9A"
                        content_url = video_res.content_url if video_res else f"https://www.youtube-nocookie.com/embed/{vid_id}"
                        
                        rec_id = f"rec-vid-{top.id}"
                        title = f"Recommended Lesson: {top.title}"
                        description = f"Watch this verified video lesson on {top.title} aligned with {board} {grade} syllabus."
                        
                        recommendations.append(
                            RecommendationItem(
                                id=rec_id,
                                title=title,
                                description=description,
                                subject=s.subject_name,
                                learning_style=style,
                                recommendation_type="recommended_video",
                                topic_id=top.id,
                                video_id=vid_id,
                                video_url=content_url,
                                duration_minutes=round((video_res.duration_seconds / 60) if video_res and video_res.duration_seconds else (top.estimated_minutes or 12)),
                            )
                        )
                        if len(recommendations) >= 6:
                            break
                    if len(recommendations) >= 6:
                        break
            if len(recommendations) >= 6:
                break

        # Fallback if no specific videos found yet
        if not recommendations:
            for s in subjects:
                rec_id = f"rec-subj-{s.id}"
                title = f"{s.subject_name}: Foundation & Concept Video"
                description = f"Recommended core overview for {grade} ({board}) in {s.subject_name}."
                recommendations.append(
                    RecommendationItem(
                        id=rec_id,
                        title=title,
                        description=description,
                        subject=s.subject_name,
                        learning_style=style,
                        recommendation_type="recommended_video",
                        topic_id=None,
                        video_id="kYJq1000m9A",
                        video_url="https://www.youtube-nocookie.com/embed/kYJq1000m9A",
                        duration_minutes=12,
                    )
                )

        return RecommendationsResponse(
            user_id=user.id,
            recommendations=recommendations,
            total_count=len(recommendations),
        )'''

assert old_func in code, "old_func not found"
code = code.replace(old_func, new_func, 1)
with open('backend/app/services/dashboard_service.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated backend/app/services/dashboard_service.py successfully")

