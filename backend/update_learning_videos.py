import re

path = 'backend/app/services/learning_service.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        # Curriculum syllabus chapter & topic generator tailored specifically to student's subject, board, and grade
        s_lower = subject_name.lower()
        if any(w in s_lower for w in ["account", "bookkeeping"]):'''

replacement = '''        # Curriculum syllabus chapter & topic generator tailored specifically to student's subject, board, and grade
        s_lower = subject_name.lower()
        if any(w in s_lower for w in ["sanskrit", "ruchira", "shemushi"]):
            curriculum_chapters = [
                {
                    "num": 1,
                    "title": f"Sanskrit Vyakaran & Varnamala (संस्कृत व्याकरणम्)",
                    "desc": f"Foundations of Sanskrit alphabet, vowels, consonants, and word synthesis according to {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": "Varnamala & Uchcharan Sthan (वर्णमाला एवं उच्चारण-स्थानम्)", "desc": "Sanskrit swara, vyanjana, and articulation positions.", "minutes": 20, "video_id": "T6o6WkQ54pE"},
                        {"num": 2, "title": "Shabd Roop & Karak Parichay (शब्दरूपाणि कारक-परिचयश्च)", "desc": "Vibhakti, declensions, and basic noun declension forms.", "minutes": 24, "video_id": "u5n_2w03q_8"},
                    ],
                },
                {
                    "num": 2,
                    "title": f"Dhatu Roop & Simple Sentence Construction (धातुरूपाणि वाक्यरचना च)",
                    "desc": f"Lakar usage (Lat, Lrit, Lang), verb conjugations, and translation essentials.",
                    "topics": [
                        {"num": 1, "title": "Dhatu Roop - Lat & Lrit Lakar (लट् एवं लृट् लकारः)", "desc": "Present and future tense verbal conjugations and practice.", "minutes": 25, "video_id": "4iZ0UvXyFvE"},
                        {"num": 2, "title": "Anuvad & Pathya Pustak Abhyas (अनुवादः पाठ्याभ्यासश्च)", "desc": "Sentence translations and comprehension exercise analysis.", "minutes": 28, "video_id": "T6o6WkQ54pE"},
                    ],
                },
            ]
        elif any(w in s_lower for w in ["hindi"]):
            curriculum_chapters = [
                {
                    "num": 1,
                    "title": f"Hindi Vyakaran: Bhasha aur Vyakaran (भाषा एवं व्याकरण)",
                    "desc": f"Core grammar rules, varn-vichar, sandhi, and shabd bhed for {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": "Varn Vichar & Sandhi Niyam (वर्ण विचार एवं संधि नियम)", "desc": "Phonetics, vowel joins, and consonant transformations.", "minutes": 20, "video_id": "qR812uE16kE"},
                        {"num": 2, "title": "Sangya, Sarvanam & Karak (संज्ञा, सर्वनाम एवं कारक)", "desc": "Noun categories, pronouns, case markers, and practical syntax.", "minutes": 24, "video_id": "qR812uE16kE"},
                    ],
                },
                {
                    "num": 2,
                    "title": f"Hindi Sahitya & Pathan Bodh (साहित्य एवं पठन बोध)",
                    "desc": f"Prose, poetry comprehension, character insights, and answer writing format.",
                    "topics": [
                        {"num": 1, "title": "Gadya Khand & Bhaav Bodh (गद्य खंड एवं भाव बोध)", "desc": "Critical appreciation and central themes of prescribed chapters.", "minutes": 25, "video_id": "qR812uE16kE"},
                        {"num": 2, "title": "Kavya Soundarya & Vyakhya (काव्य सौंदर्य एवं व्याख्या)", "desc": "Poetic devices, meter, and stanza explanations.", "minutes": 28, "video_id": "qR812uE16kE"},
                    ],
                },
            ]
        elif any(w in s_lower for w in ["english", "literature"]):
            curriculum_chapters = [
                {
                    "num": 1,
                    "title": f"English Language, Grammar & Comprehension",
                    "desc": f"Applied grammar, tense agreements, active-passive voice, and reading skills for {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": "Tenses, Subject-Verb Concord & Clauses", "desc": "Grammatical harmony, conditional clauses, and error correction.", "minutes": 20, "video_id": "JULrwhkY6eM"},
                        {"num": 2, "title": "Reading Comprehension & Contextual Vocabulary", "desc": "Passage skimming, inference deduction, and word power.", "minutes": 24, "video_id": "JULrwhkY6eM"},
                    ],
                },
                {
                    "num": 2,
                    "title": f"Prose Analysis & Structured Creative Writing",
                    "desc": f"Essay writing, letter drafting, character analysis, and literary appreciation.",
                    "topics": [
                        {"num": 1, "title": "Formal Writing: Letters, Notices & Analytical Essays", "desc": "Standard templates, formatting, and high-scoring structures.", "minutes": 25, "video_id": "JULrwhkY6eM"},
                        {"num": 2, "title": "Literature Study: Themes, Motifs & Poetic Devices", "desc": "Understanding narrative arc, character motives, and metaphor analysis.", "minutes": 28, "video_id": "JULrwhkY6eM"},
                    ],
                },
            ]
        elif any(w in s_lower for w in ["account", "bookkeeping"]):'''

if target in text:
    text = text.replace(target, replacement, 1)
    print("Replaced subject chapters")
else:
    print("Subject chapters target not found")

fallback_target = '''            curriculum_chapters = [
                {
                    "num": 1,
                    "title": f"Foundations & Key Concepts of {subject_name}",
                    "desc": f"Core syllabus framework and syllabus terminology according to {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": f"Core Essentials of {subject_name}", "desc": f"Foundational rules, syllabus scope, and terminology.", "minutes": 20, "video_id": "nbuM0aJjVgE"},
                        {"num": 2, "title": f"Fundamental Rules & Thematic Structure", "desc": f"In-depth breakdown of standard board-prescribed methodologies.", "minutes": 24, "video_id": "nbuM0aJjVgE"},
                    ],
                },
                {
                    "num": 2,
                    "title": f"Advanced Themes & Board Exam Preparation",
                    "desc": f"High-yield curriculum modules, practical applications, and syllabus problem-solving.",
                    "topics": [
                        {"num": 1, "title": f"Analytical Concepts & Applied Scenarios", "desc": f"Connecting foundational theories to examination scoring.", "minutes": 25, "video_id": "nbuM0aJjVgE"},
                        {"num": 2, "title": f"Review & Marking Scheme Synthesis", "desc": f"Official evaluation guidelines and step-by-step scoring.", "minutes": 28, "video_id": "nbuM0aJjVgE"},
                    ],
                },
            ]'''

fallback_replacement = '''            # General fallback educational video tailored to subject
            gen_video_id = "T6o6WkQ54pE" if "sanskrit" in s_lower else ("qR812uE16kE" if "hindi" in s_lower else ("9bZkp7q19f0" if "math" in s_lower else ("yE8rkG9Dw4s" if any(w in s_lower for w in ["sci", "bio", "chem", "phys"]) else "JULrwhkY6eM")))
            curriculum_chapters = [
                {
                    "num": 1,
                    "title": f"Foundations & Key Concepts of {subject_name}",
                    "desc": f"Core syllabus framework and syllabus terminology according to {board} {grade}.",
                    "topics": [
                        {"num": 1, "title": f"Core Essentials of {subject_name}", "desc": f"Foundational rules, syllabus scope, and terminology.", "minutes": 20, "video_id": gen_video_id},
                        {"num": 2, "title": f"Fundamental Rules & Thematic Structure", "desc": f"In-depth breakdown of standard board-prescribed methodologies.", "minutes": 24, "video_id": gen_video_id},
                    ],
                },
                {
                    "num": 2,
                    "title": f"Advanced Themes & Board Exam Preparation",
                    "desc": f"High-yield curriculum modules, practical applications, and syllabus problem-solving.",
                    "topics": [
                        {"num": 1, "title": f"Analytical Concepts & Applied Scenarios", "desc": f"Connecting foundational theories to examination scoring.", "minutes": 25, "video_id": gen_video_id},
                        {"num": 2, "title": f"Review & Marking Scheme Synthesis", "desc": f"Official evaluation guidelines and step-by-step scoring.", "minutes": 28, "video_id": gen_video_id},
                    ],
                },
            ]'''

if fallback_target in text:
    text = text.replace(fallback_target, fallback_replacement, 1)
    print("Replaced fallback chapters")
else:
    print("Fallback target not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated learning_service.py successfully!")

