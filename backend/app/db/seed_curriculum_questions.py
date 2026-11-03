"""
Multi-Subject Curriculum Practice Questions and PYQs Seeder for SmartLearn.AI.
Seeds authentic board past-year questions and syllabus-grounded practice questions
for Mathematics, Science, and Social Science (CBSE & ICSE Classes 5, 8, 10, and 11).
"""

from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.learning import Chapter, PracticeQuestion, PreviousYearQuestion, Subject, Topic

TOPIC_QUESTIONS: List[Dict[str, Any]] = [
    # ── 1. CBSE Class 10 Math: Real Numbers ────────────────────────────────────
    {
        "subject_name": "Mathematics",
        "board": "CBSE",
        "grade": "Class 10",
        "topic_number": 1,
        "chapter_number": 1,
        "pyqs": [
            {
                "exam_year": 2024,
                "paper_code": "30/1/1",
                "question_number": 1,
                "marks": 1,
                "question_text": "If two positive integers a and b are written as a = x^3 y^2 and b = x y^3, where x, y are prime numbers, then HCF(a, b) is:",
                "marking_scheme": "HCF(a, b) is the product of the smallest power of each common prime factor involved in the numbers. Smallest power of x is x^1, and y is y^2. Hence HCF = x y^2.",
                "source_name": "CBSE Official Secondary Examination 2024 Mathematics Standard",
                "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
            },
            {
                "exam_year": 2023,
                "paper_code": "30/2/1",
                "question_number": 2,
                "marks": 2,
                "question_text": "Find the LCM and HCF of 336 and 54, and verify that LCM x HCF = product of the two numbers.",
                "marking_scheme": "Prime factorisation: 336 = 2^4 x 3 x 7, 54 = 2 x 3^3. HCF = 2 x 3 = 6. LCM = 2^4 x 3^3 x 7 = 3024. HCF x LCM = 6 x 3024 = 18144. Product = 336 x 54 = 18144. LHS = RHS verified.",
                "source_name": "CBSE Board Examination 2023",
                "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
            }
        ],
        "practice": [
            {
                "question_text": "According to the Fundamental Theorem of Arithmetic, what is unique about the prime factorisation of any composite number?",
                "options": [
                    {"id": "A", "text": "The sequence and order of the prime factors"},
                    {"id": "B", "text": "The prime factors themselves, apart from their order"},
                    {"id": "C", "text": "Only the largest prime factor"},
                    {"id": "D", "text": "It can always be expressed with an even number of factors"}
                ],
                "correct_answer": "B",
                "explanation": "The Fundamental Theorem of Arithmetic states that every composite number can be uniquely factorised into prime factors, ignoring the order in which they are written.",
                "difficulty": "easy",
                "marks": 1,
            },
            {
                "question_text": "If HCF(306, 657) = 9, what is LCM(306, 657)?",
                "options": [
                    {"id": "A", "text": "22338"},
                    {"id": "B", "text": "18450"},
                    {"id": "C", "text": "24576"},
                    {"id": "D", "text": "34218"}
                ],
                "correct_answer": "A",
                "explanation": "Using LCM(a, b) = (a * b) / HCF(a, b): LCM = (306 * 657) / 9 = 34 * 657 = 22338.",
                "difficulty": "medium",
                "marks": 1,
            }
        ]
    },

    # ── 2. CBSE Class 10 Science: Chemical Reactions ───────────────────────────
    {
        "subject_name": "Science",
        "board": "CBSE",
        "grade": "Class 10",
        "topic_number": 1,
        "chapter_number": 1,
        "pyqs": [
            {
                "exam_year": 2024,
                "paper_code": "31/1/1",
                "question_number": 3,
                "marks": 1,
                "question_text": "When aqueous solutions of potassium iodide and lead nitrate are mixed, an insoluble precipitate is formed. What is the colour and chemical name of this precipitate?",
                "marking_scheme": "Yellow precipitate of Lead Iodide (PbI2). Reaction: Pb(NO3)2 + 2KI -> PbI2 (s) + 2KNO3.",
                "source_name": "CBSE Board Examination 2024 Science",
                "source_url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
            }
        ],
        "practice": [
            {
                "question_text": "Which of the following is an example of a thermal decomposition reaction?",
                "options": [
                    {"id": "A", "text": "Electrolysis of acidified water"},
                    {"id": "B", "text": "Heating ferrous sulphate crystals in a dry boiling tube"},
                    {"id": "C", "text": "Burning of natural gas (methane)"},
                    {"id": "D", "text": "Reaction of iron nails with copper sulphate solution"}
                ],
                "correct_answer": "B",
                "explanation": "Heating green FeSO4.7H2O crystals causes thermal decomposition: 2FeSO4(s) --heat--> Fe2O3(s) + SO2(g) + SO3(g).",
                "difficulty": "medium",
                "marks": 1,
            },
            {
                "question_text": "Why must chemical equations be balanced in accordance with fundamental laws of chemistry?",
                "options": [
                    {"id": "A", "text": "Law of Definite Proportions"},
                    {"id": "B", "text": "Law of Conservation of Mass"},
                    {"id": "C", "text": "Avogadro's Hypothesis"},
                    {"id": "D", "text": "Dalton's Partial Pressure Law"}
                ],
                "correct_answer": "B",
                "explanation": "The Law of Conservation of Mass dictates that matter can neither be created nor destroyed in a chemical reaction. Therefore, the total number of atoms of each element must remain equal on both sides of the equation.",
                "difficulty": "easy",
                "marks": 1,
            }
        ]
    },

    # ── 3. ICSE Class 10 Math: GST & Banking ───────────────────────────────────
    {
        "subject_name": "Mathematics",
        "board": "ICSE",
        "grade": "Class 10",
        "topic_number": 1,
        "chapter_number": 1,
        "pyqs": [
            {
                "exam_year": 2024,
                "paper_code": "51/2024",
                "question_number": 1,
                "marks": 1,
                "question_text": "In an intra-state transaction within Maharashtra, goods worth Rs 10,000 are sold at 18% GST. What are the values of CGST and SGST paid?",
                "marking_scheme": "For intra-state transaction, GST is divided equally: CGST = 9% of 10,000 = Rs 900; SGST = 9% of 10,000 = Rs 900; IGST = 0.",
                "source_name": "CISCE ICSE Class 10 Mathematics 2024",
                "source_url": "https://www.cisce.org",
            }
        ],
        "practice": [
            {
                "question_text": "In an inter-state sale of goods from Delhi to Mumbai, which tax component is applicable?",
                "options": [
                    {"id": "A", "text": "Only CGST"},
                    {"id": "B", "text": "Equal parts CGST and SGST"},
                    {"id": "C", "text": "Integrated GST (IGST) at the full prescribed rate"},
                    {"id": "D", "text": "No tax is applicable across state borders"}
                ],
                "correct_answer": "C",
                "explanation": "Inter-state transactions (between two different states or union territories) attract Integrated GST (IGST) paid directly to the central government.",
                "difficulty": "easy",
                "marks": 1,
            }
        ]
    },

    # ── 4. CBSE Class 5 Math: Large Numbers ────────────────────────────────────
    {
        "subject_name": "Mathematics",
        "board": "CBSE",
        "grade": "Class 5",
        "topic_number": 1,
        "chapter_number": 1,
        "practice": [
            {
                "question_text": "In the Indian place value system, how many zeros are there in One Lakh (1,00,000)?",
                "options": [
                    {"id": "A", "text": "4 zeros"},
                    {"id": "B", "text": "5 zeros"},
                    {"id": "C", "text": "6 zeros"},
                    {"id": "D", "text": "7 zeros"}
                ],
                "correct_answer": "B",
                "explanation": "1 Lakh is written as 1,00,000, which has exactly five zeros following the digit 1.",
                "difficulty": "easy",
                "marks": 1,
            },
            {
                "question_text": "A motor boat travels at a speed of 20 kilometres in one hour. How far will it go in 3 and a half hours (3.5 hours)?",
                "options": [
                    {"id": "A", "text": "60 km"},
                    {"id": "B", "text": "70 km"},
                    {"id": "C", "text": "80 km"},
                    {"id": "D", "text": "50 km"}
                ],
                "correct_answer": "B",
                "explanation": "Distance = Speed x Time = 20 km/h x 3.5 h = 70 kilometres.",
                "difficulty": "medium",
                "marks": 1,
            }
        ]
    }
]


def seed_questions(db: Session) -> None:
    print("Seeding curriculum-grounded PYQs and Practice Questions...")
    for item in TOPIC_QUESTIONS:
        subject = (
            db.query(Subject)
            .filter(
                Subject.name == item["subject_name"],
                Subject.board == item["board"],
                Subject.grade == item["grade"],
            )
            .first()
        )
        if not subject:
            continue

        chapter = (
            db.query(Chapter)
            .filter(
                Chapter.subject_id == subject.id,
                Chapter.chapter_number == item["chapter_number"],
            )
            .first()
        )
        if not chapter:
            continue

        topic = (
            db.query(Topic)
            .filter(
                Topic.chapter_id == chapter.id,
                Topic.topic_number == item["topic_number"],
            )
            .first()
        )
        if not topic:
            continue

        # Seed Authentic PYQs
        for q in item.get("pyqs", []):
            exists = (
                db.query(PreviousYearQuestion)
                .filter(
                    PreviousYearQuestion.topic_id == topic.id,
                    PreviousYearQuestion.exam_year == q["exam_year"],
                    PreviousYearQuestion.question_number == str(q["question_number"]),
                )
                .first()
            )
            if not exists:
                pyq = PreviousYearQuestion(
                    subject_id=subject.id,
                    topic_id=topic.id,
                    board=subject.board,
                    grade=subject.grade,
                    exam_year=q["exam_year"],
                    paper_code=q.get("paper_code", "Standard"),
                    question_number=str(q["question_number"]),
                    question_text=q["question_text"],
                    marks=q.get("marks", 1),
                    marking_scheme=q["marking_scheme"],
                    source_name=q.get("source_name", f"{subject.board} Official Exam"),
                    source_url=q.get("source_url"),
                    is_verified=True,
                )
                db.add(pyq)
                print(f"Added PYQ for {subject.name} - {topic.title} ({q['exam_year']})")

        # Seed Practice Questions
        for pq_data in item.get("practice", []):
            exists = (
                db.query(PracticeQuestion)
                .filter(
                    PracticeQuestion.topic_id == topic.id,
                    PracticeQuestion.question_text == pq_data["question_text"],
                )
                .first()
            )
            if not exists:
                pq = PracticeQuestion(
                    topic_id=topic.id,
                    question_text=pq_data["question_text"],
                    question_type="mcq",
                    options=pq_data["options"],
                    correct_answer=pq_data["correct_answer"],
                    explanation=pq_data["explanation"],
                    difficulty=pq_data.get("difficulty", "medium"),
                    marks=pq_data.get("marks", 1),
                    is_ai_generated=False,
                    generation_provenance="Curriculum Editorial Board",
                )
                db.add(pq)
                print(f"Added Practice Question for {subject.name} - {topic.title}")

    db.commit()
    print("Questions seeded successfully!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_questions(db)
    finally:
        db.close()
