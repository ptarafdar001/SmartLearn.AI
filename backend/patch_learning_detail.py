with open('backend/app/services/learning_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        resources = LearningRepository.get_resources_by_topic_id(db, topic.id, only_active=True)
        resource_responses = ['''

replacement = '''        resources = LearningRepository.get_resources_by_topic_id(db, topic.id, only_active=True)

        # Dynamic YouTube Video Recommendation integration
        # Search specifically for this board, grade, subject, chapter, and topic
        profile = OnboardingRepository.get_student_profile(db, user_id)
        pref = OnboardingRepository.get_learning_preference(db, user_id)
        board_val = (subject.board if subject and subject.board else (profile.board if profile else None))
        grade_val = (subject.grade if subject and subject.grade else (profile.grade if profile else None))
        pref_lang = pref.preferred_language if pref and hasattr(pref, "preferred_language") else "English"

        has_verified_video = any(r.resource_type == "video" and r.external_id and len(r.external_id) == 11 for r in resources)
        if not has_verified_video or any(r.external_id in ["nbuM0aJjVgE", "kYJq1000m9A"] for r in resources if r.resource_type == "video"):
            try:
                from app.services.youtube_service import YouTubeService
                yt_recs = YouTubeService.search_videos(
                    subject=subject.name if subject else "General Studies",
                    topic=topic.title,
                    chapter=chapter.title if chapter else None,
                    board=board_val,
                    grade=grade_val,
                    language=pref_lang,
                    max_results=3,
                )
                if yt_recs:
                    best_yt = yt_recs[0]
                    # Update or add video resource in DB
                    existing_vid = next((r for r in resources if r.resource_type == "video"), None)
                    if existing_vid:
                        existing_vid.external_id = best_yt.video_id
                        existing_vid.content_url = best_yt.embed_url
                        existing_vid.title = f"Video Lesson: {best_yt.title}"
                        existing_vid.source_name = best_yt.channel_title
                        existing_vid.duration_seconds = best_yt.duration_minutes * 60
                        db.commit()
                        db.refresh(existing_vid)
                    else:
                        from app.models.learning import LearningResource
                        new_vid = LearningResource(
                            topic_id=topic.id,
                            title=f"Video Lesson: {best_yt.title}",
                            resource_type="video",
                            provider="YouTube",
                            source_name=best_yt.channel_title,
                            external_id=best_yt.video_id,
                            content_url=best_yt.embed_url,
                            duration_seconds=best_yt.duration_minutes * 60,
                            language=pref_lang or "English",
                            order_index=1,
                            is_active=True,
                            is_verified=True,
                        )
                        db.add(new_vid)
                        db.commit()
                    resources = LearningRepository.get_resources_by_topic_id(db, topic.id, only_active=True)
            except Exception as e:
                logger.warning(f"Error fetching dynamic topic video: {e}")

        resource_responses = ['''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('backend/app/services/learning_service.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated get_topic_detail in learning_service.py")
else:
    print("Target not found in learning_service.py")

