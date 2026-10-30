import sys
sys.path.insert(0, 'backend')
from app.db.session import SessionLocal
from app.models.learning import Subject, LearningResource, Chapter, Topic

db = SessionLocal()

VIDEO_MAP = {
    'sanskrit': 'T6o6WkQ54pE',
    'hindi': 'qR812uE16kE',
    'english': 'JULrwhkY6eM',
    'mathematics': '9bZkp7q19f0',
    'math': '9bZkp7q19f0',
    'science': 'yE8rkG9Dw4s',
    'biology': 'yE8rkG9Dw4s',
    'physics': 'yE8rkG9Dw4s',
    'chemistry': 'yE8rkG9Dw4s',
    'economics': '1uP8h0s5UaY',
    'accountancy': '9bZkp7q19f0',
    'commerce': '9bZkp7q19f0',
    'business': '9bZkp7q19f0',
}

subjects = db.query(Subject).all()
updated_count = 0

for s in subjects:
    s_name_lower = s.name.lower()
    chosen_vid = None
    for k, v in VIDEO_MAP.items():
        if k in s_name_lower:
            chosen_vid = v
            break
            
    if not chosen_vid:
        continue
        
    resources = (
        db.query(LearningResource)
        .join(Topic)
        .join(Chapter)
        .filter(Chapter.subject_id == s.id, LearningResource.resource_type == 'video')
        .all()
    )
    for r in resources:
        if r.external_id != chosen_vid:
            print(f"Updating Subject '{s.name}' Resource '{r.title}': {r.external_id} -> {chosen_vid}")
            r.external_id = chosen_vid
            r.content_url = f"https://www.youtube-nocookie.com/embed/{chosen_vid}"
            updated_count += 1

db.commit()
print(f"Successfully updated {updated_count} video resources in the database.")
db.close()

