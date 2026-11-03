with open('backend/app/services/practice_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        prompt = (
            f"Generate 3 new educational multiple-choice practice questions (MCQs) for:\\n"
            f"Subject: {bundle.subject.name} ({bundle.subject.board} {bundle.subject.grade})\\n"
            f"Topic: {bundle.topic.title}\\n\\n"
            f"CURRICULUM GROUNDING EVIDENCE:\\n{evidence_text}\\n\\n"
            f"Requirements:\\n"
            f"1. Generate strictly 3 MCQs in valid JSON format.\\n"'''

replacement = '''        prompt = (
            f"Generate strictly 10 comprehensive educational multiple-choice practice questions (MCQs) for:\\n"
            f"Subject: {bundle.subject.name} ({bundle.subject.board} {bundle.subject.grade})\\n"
            f"Topic: {bundle.topic.title}\\n\\n"
            f"CURRICULUM GROUNDING EVIDENCE:\\n{evidence_text}\\n\\n"
            f"Requirements:\\n"
            f"1. Generate strictly 10 distinct, syllabus-aligned MCQs covering foundational theory, definitions, applications, and problem-solving.\\n"'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('backend/app/services/practice_service.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated practice_service.py to 10 questions successfully")
else:
    print("Target prompt not found in practice_service.py")

