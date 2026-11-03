import sys

with open('backend/app/schemas/dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """class RecommendationItem(BaseModel):
    \"\"\"A deterministic, data-driven study recommendation derived from the student's profile.\"\"\"
    id: str
    title: str
    description: str
    subject: str
    learning_style: Optional[str] = None
    recommendation_type: str"""

replacement = """class RecommendationItem(BaseModel):
    \"\"\"A deterministic, data-driven study recommendation derived from the student's profile.\"\"\"
    id: str
    title: str
    description: str
    subject: str
    learning_style: Optional[str] = None
    recommendation_type: str
    topic_id: Optional[int] = None
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('backend/app/schemas/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated backend/app/schemas/dashboard.py successfully")
else:
    print("Target not found in schemas/dashboard.py")

