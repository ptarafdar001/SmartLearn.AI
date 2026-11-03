with open('backend/app/api/learning/routes.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoint_code = '''

@router.get(
    "/topics/{topic_id}/video-recommendations",
    summary="Get dynamic YouTube video recommendations tailored to topic and curriculum",
)
def get_topic_video_recommendations(
    topic_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Dynamically searches YouTube and returns ranked educational videos aligned
    specifically with the student's board, class, subject, chapter, and topic.
    """
    topic = LearningRepository.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
    subject = LearningRepository.get_subject_by_id(db, chapter.subject_id) if chapter else None

    from app.repositories.onboarding_repository import OnboardingRepository
    from app.services.youtube_service import YouTubeService

    profile = OnboardingRepository.get_student_profile(db, current_user.id)
    pref = OnboardingRepository.get_learning_preference(db, current_user.id)

    board = subject.board if subject and subject.board else (profile.board if profile else None)
    grade = subject.grade if subject and subject.grade else (profile.grade if profile else None)
    language = pref.preferred_language if pref and hasattr(pref, "preferred_language") else "English"

    videos = YouTubeService.search_videos(
        subject=subject.name if subject else "General Studies",
        topic=topic.title,
        chapter=chapter.title if chapter else None,
        board=board,
        grade=grade,
        language=language,
        max_results=6,
    )

    return {
        "topic_id": topic.id,
        "topic_title": topic.title,
        "chapter_title": chapter.title if chapter else None,
        "subject_name": subject.name if subject else None,
        "board": board,
        "grade": grade,
        "videos": [
            {
                "video_id": v.video_id,
                "title": v.title,
                "description": v.description,
                "channel_title": v.channel_title,
                "thumbnail_url": v.thumbnail_url,
                "embed_url": v.embed_url,
                "duration_minutes": v.duration_minutes,
                "relevance_score": v.relevance_score,
            }
            for v in videos
        ],
        "total_count": len(videos),
    }
'''

if "/topics/{topic_id}/video-recommendations" not in text:
    text += endpoint_code
    with open('backend/app/api/learning/routes.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added /topics/{topic_id}/video-recommendations endpoint")
else:
    print("Endpoint already exists")

