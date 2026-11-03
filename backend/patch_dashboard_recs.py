with open('backend/app/services/dashboard_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                        resources = LearningRepository.get_resources_by_topic_id(db, top.id, only_active=True)
                        video_res = next((r for r in resources if r.resource_type == "video"), None)
                        
                        vid_id = video_res.external_id if video_res else "kYJq1000m9A"
                        content_url = video_res.content_url if video_res else f"https://www.youtube-nocookie.com/embed/{vid_id}"
                        
                        rec_id = f"rec-vid-{top.id}"
                        title = f"Recommended Lesson: {top.title}"
                        description = f"Watch this verified video lesson on {top.title} aligned with {board} {grade} syllabus."'''

replacement = '''                        resources = LearningRepository.get_resources_by_topic_id(db, top.id, only_active=True)
                        video_res = next((r for r in resources if r.resource_type == "video"), None)
                        
                        # Query dynamic YouTube recommendation if video is missing or generic
                        vid_id = video_res.external_id if video_res else None
                        content_url = video_res.content_url if video_res else None
                        vid_title = f"Recommended Lesson: {top.title}"
                        
                        if not vid_id or vid_id in ["nbuM0aJjVgE", "kYJq1000m9A"]:
                            try:
                                from app.services.youtube_service import YouTubeService
                                yt_results = YouTubeService.search_videos(
                                    subject=s.subject_name,
                                    topic=top.title,
                                    chapter=ch.title,
                                    board=board,
                                    grade=grade,
                                    max_results=1,
                                )
                                if yt_results:
                                    yt = yt_results[0]
                                    vid_id = yt.video_id
                                    content_url = yt.embed_url
                                    vid_title = yt.title
                                    # Sync back to resource
                                    if video_res:
                                        video_res.external_id = vid_id
                                        video_res.content_url = content_url
                                        video_res.title = f"Video Lesson: {yt.title}"
                                        db.commit()
                            except Exception:
                                pass
                        
                        if not vid_id:
                            vid_id = "T6o6WkQ54pE" if "sanskrit" in s.subject_name.lower() else "9bZkp7q19f0"
                            content_url = f"https://www.youtube-nocookie.com/embed/{vid_id}"

                        rec_id = f"rec-vid-{top.id}"
                        title = vid_title
                        description = f"Watch this verified video lesson on {top.title} aligned with {board} {grade} syllabus."'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('backend/app/services/dashboard_service.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated get_recommendations with dynamic YouTubeService search in dashboard_service.py")
else:
    print("Target not found in dashboard_service.py")

