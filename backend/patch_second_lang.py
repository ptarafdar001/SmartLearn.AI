with open('backend/app/services/learning_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        elif any(w in s_lower for w in ["economic", "eco"]):'''

replacement = '''        elif any(w in s_lower for w in ["second language", "2nd language", "language ii"]):
            curriculum_chapters = [
                {
                    "num": 1,
                    "title": f"{subject_name}: Vyakaran & Bhasha Bodh (भाषा एवं व्याकरण)",
                    "desc": f"Grammar rules, sentence syntax, comprehension, and vocabulary prescribed for {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": f"Vyakaran Niyam & Shabda Rachna (व्याकरण एवं शब्द रचना)", "desc": "Foundational grammar, morphology, and conjugation principles.", "minutes": 20, "video_id": "qR812uE16kE"},
                        {"num": 2, "title": f"Vakya Vinyas & Anuvad (वाक्य विन्यास एवं अनुवाद)", "desc": "Sentence formation, idioms, case inflection, and translation.", "minutes": 24, "video_id": "T6o6WkQ54pE"},
                    ],
                },
                {
                    "num": 2,
                    "title": f"{subject_name}: Sahitya & Pathan Bodh (साहित्य एवं पठन-बोध)",
                    "desc": f"Prescribed prose, poetry, textual interpretation, and question answers for {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": f"Gadya & Bhaavarth (गद्य एवं भावार्थ)", "desc": "Prose textual comprehension, central theme analysis, and summary.", "minutes": 25, "video_id": "qR812uE16kE"},
                        {"num": 2, "title": f"Kavya & Vyakhya (काव्य एवं व्याख्या)", "desc": "Poetic appreciation, verse analysis, and critical thinking.", "minutes": 28, "video_id": "T6o6WkQ54pE"},
                    ],
                },
            ]
        elif any(w in s_lower for w in ["economic", "eco"]) and not any(w in s_lower for w in ["second", "language"]):'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('backend/app/services/learning_service.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated learning_service.py with Second Language curriculum")
else:
    print("Target not found in learning_service.py")

