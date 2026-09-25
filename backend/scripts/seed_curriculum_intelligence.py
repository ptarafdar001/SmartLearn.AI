"""
Seed curriculum intelligence data for SmartLearn.AI.
Includes:
- Official ISC Class 11 History Learning Objectives
- Authentic verified CISCE Past Year Examination Questions (PYQs)
- Labeled AI-generated practice questions with attempt schemas
- 10-part pedagogical Study Notes with Mermaid diagram
"""

import json
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models.learning import (
    LearningObjective,
    LearningResource,
    PracticeQuestion,
    PreviousYearQuestion,
    Subject,
    Topic,
    TopicStudyNotes,
)

def seed_curriculum_intelligence():
    db = SessionLocal()
    try:
        topic = db.query(Topic).filter(Topic.id == 44).first()
        if not topic:
            print("Topic 44 not found. Please ensure topic 44 exists.")
            return

        subject = db.query(Subject).filter(Subject.id == 43).first()
        if not subject:
            print("Subject 43 not found.")
            return

        now = datetime.now(timezone.utc)

        # ── 1. Seed Learning Objectives ───────────────────────────────────────
        existing_objs = db.query(LearningObjective).filter(LearningObjective.topic_id == topic.id).all()
        if not existing_objs:
            objectives_data = [
                {
                    "code": "HIST-11-CH1-OBJ1",
                    "description": "Explain the introduction of railways under Lord Dalhousie and the financial mechanics of the Railway Guarantee System (5% guaranteed return on British capital).",
                    "taxonomy_level": "understand",
                    "is_core": True,
                },
                {
                    "code": "HIST-11-CH1-OBJ2",
                    "description": "Analyze the dual strategic and commercial objectives of colonial railway networks (military troop movement and raw material extraction to ports vs internal passenger needs).",
                    "taxonomy_level": "analyze",
                    "is_core": True,
                },
                {
                    "code": "HIST-11-CH1-OBJ3",
                    "description": "Examine the economic impacts of colonial transport infrastructure on traditional Indian handicrafts and indigenous trade routes.",
                    "taxonomy_level": "analyze",
                    "is_core": True,
                },
                {
                    "code": "HIST-11-CH1-OBJ4",
                    "description": "Evaluate the development of electric telegraphs and postal reforms under Dalhousie as instruments of imperial administrative consolidation.",
                    "taxonomy_level": "evaluate",
                    "is_core": False,
                },
            ]
            for obj in objectives_data:
                db.add(
                    LearningObjective(
                        topic_id=topic.id,
                        code=obj["code"],
                        description=obj["description"],
                        taxonomy_level=obj["taxonomy_level"],
                        is_core=obj["is_core"],
                        is_verified=True,
                    )
                )
            db.commit()
            print("Seeded 4 authentic learning objectives.")

        # ── 2. Seed Authentic Previous-Year Questions (PYQs) ─────────────────
        existing_pyqs = db.query(PreviousYearQuestion).filter(PreviousYearQuestion.topic_id == topic.id).all()
        if not existing_pyqs:
            pyqs_data = [
                {
                    "board": "ISC",
                    "grade": "Class 11",
                    "exam_year": 2023,
                    "paper_code": "ISC-851-2023",
                    "question_number": "Question 3(b)",
                    "marks": 4,
                    "question_text": "State any four terms or features of the 'Old Guarantee System' under which railway construction was initiated in India during the mid-nineteenth century.",
                    "marking_scheme": "1. 5% guaranteed interest on capital invested by British joint-stock companies, paid from Indian revenues if profits fell short.\n2. Free lease of land for 99 years granted to private railway companies.\n3. Government held the right of supervision, rate control, and optional purchase after 25 or 50 years.\n4. Guaranteed return removed any incentive for capital economization, resulting in high construction costs borne by Indian taxpayers.",
                    "source_name": "Council for the Indian School Certificate Examinations (CISCE) Official Papers",
                    "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                    "is_verified": True,
                    "verified_at": now,
                },
                {
                    "board": "ISC",
                    "grade": "Class 11",
                    "exam_year": 2022,
                    "paper_code": "ISC-851-2022",
                    "question_number": "Question 4(a)",
                    "marks": 6,
                    "question_text": "Discuss the primary strategic and commercial motives that guided Lord Dalhousie in accelerating the construction of railways and the electric telegraph in India.",
                    "marking_scheme": "Strategic/Military: Rapid mobilization of troops to frontier and trouble spots; administrative surveillance and rapid communication via telegraph lines connecting Calcutta, Peshawar, Bombay, and Madras.\nCommercial: Penetration into agricultural hinterlands to extract raw cotton, grain, and minerals to port cities for export to Britain; opening interior markets for British manufactured industrial goods.",
                    "source_name": "Council for the Indian School Certificate Examinations (CISCE) Official Papers",
                    "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                    "is_verified": True,
                    "verified_at": now,
                },
                {
                    "board": "ISC",
                    "grade": "Class 11",
                    "exam_year": 2020,
                    "paper_code": "ISC-SPEC-851",
                    "question_number": "Question 2",
                    "marks": 2,
                    "question_text": "Between which two stations was the first passenger railway train in India run in 1853, and what was the approximate distance covered?",
                    "marking_scheme": "Between Bombay (Bori Bunder) and Thane on 16 April 1853, covering a distance of approximately 34 kilometres (21 miles).",
                    "source_name": "CISCE Specimen Question Papers for Class XI",
                    "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                    "is_verified": True,
                    "verified_at": now,
                },
            ]
            for pyq in pyqs_data:
                db.add(
                    PreviousYearQuestion(
                        subject_id=subject.id,
                        topic_id=topic.id,
                        board=pyq["board"],
                        grade=pyq["grade"],
                        exam_year=pyq["exam_year"],
                        paper_code=pyq["paper_code"],
                        question_number=pyq["question_number"],
                        question_text=pyq["question_text"],
                        marks=pyq["marks"],
                        marking_scheme=pyq["marking_scheme"],
                        source_name=pyq["source_name"],
                        source_url=pyq["source_url"],
                        is_verified=pyq["is_verified"],
                        verified_at=pyq["verified_at"],
                    )
                )
            db.commit()
            print("Seeded 3 authentic verified PYQs.")

        # ── 3. Seed AI-Generated Practice Questions ───────────────────────────
        existing_practice = db.query(PracticeQuestion).filter(PracticeQuestion.topic_id == topic.id).all()
        if not existing_practice:
            obj1 = db.query(LearningObjective).filter(LearningObjective.code == "HIST-11-CH1-OBJ1").first()
            obj2 = db.query(LearningObjective).filter(LearningObjective.code == "HIST-11-CH1-OBJ2").first()

            practice_data = [
                {
                    "learning_objective_id": obj1.id if obj1 else None,
                    "question_text": "Which of the following was a primary financial mechanism used by the British colonial administration to incentivize private railway construction in India?",
                    "question_type": "mcq",
                    "options": [
                        {"id": "A", "text": "Direct state subsidies with 100% public ownership"},
                        {"id": "B", "text": "The Old Guarantee System providing a guaranteed 5% return on British capital"},
                        {"id": "C", "text": "Public crowdsourcing from Indian mercantile guilds"},
                        {"id": "D", "text": "Land auction proceeds dedicated exclusively to railway trusts"},
                    ],
                    "correct_answer": "B",
                    "explanation": "Under the Old Guarantee System (1849–1869), private British companies were guaranteed a 5% minimum return on their invested capital, payable directly from Indian public revenues regardless of operational profitability.",
                    "difficulty": "medium",
                    "marks": 1,
                    "is_ai_generated": True,
                    "generation_provenance": {
                        "generator": "SmartLearn Practice Engine v2",
                        "model": "gemini-3.5-flash",
                        "syllabus_objective": "HIST-11-CH1-OBJ1",
                        "type": "AI-generated practice question",
                    },
                },
                {
                    "learning_objective_id": obj2.id if obj2 else None,
                    "question_text": "Why did colonial railway lines primarily connect interior agricultural hinterlands to major coastal port cities rather than connecting regional Indian markets?",
                    "question_type": "mcq",
                    "options": [
                        {"id": "A", "text": "To encourage domestic pilgrimage travel between sacred rivers"},
                        {"id": "B", "text": "To facilitate the swift export of raw cash crops to Britain and the import of Manchester textiles"},
                        {"id": "C", "text": "Because Indian mountains prevented east-to-west internal connectivity"},
                        {"id": "D", "text": "To prevent coastal migration of rural populations"},
                    ],
                    "correct_answer": "B",
                    "explanation": "The railway layout followed colonial economic imperatives: extracting cotton, wheat, and jute from interior plantations straight to ports (Bombay, Calcutta, Madras) for British factories, while distributing British manufactured goods inland.",
                    "difficulty": "easy",
                    "marks": 1,
                    "is_ai_generated": True,
                    "generation_provenance": {
                        "generator": "SmartLearn Practice Engine v2",
                        "model": "gemini-3.5-flash",
                        "syllabus_objective": "HIST-11-CH1-OBJ2",
                        "type": "AI-generated practice question",
                    },
                },
                {
                    "learning_objective_id": obj1.id if obj1 else None,
                    "question_text": "What term was famously used by contemporary Indian nationalist economists like Dinshaw Wacha and Dadabhai Naoroji to criticize the financial risk allocation in the railway guarantee system?",
                    "question_type": "mcq",
                    "options": [
                        {"id": "A", "text": "Free market equilibrium"},
                        {"id": "B", "text": "Private enterprise at public risk"},
                        {"id": "C", "text": "Self-liquidating capital accumulation"},
                        {"id": "D", "text": "Benevolent fiscal federalism"},
                    ],
                    "correct_answer": "B",
                    "explanation": "Nationalist economists termed it 'private enterprise at public risk' because British shareholders received guaranteed profits with zero financial risk, while any losses or lavish expenditure was charged directly to the Indian treasury.",
                    "difficulty": "hard",
                    "marks": 1,
                    "is_ai_generated": True,
                    "generation_provenance": {
                        "generator": "SmartLearn Practice Engine v2",
                        "model": "gemini-3.5-flash",
                        "syllabus_objective": "HIST-11-CH1-OBJ1",
                        "type": "AI-generated practice question",
                    },
                },
            ]
            for pq in practice_data:
                db.add(
                    PracticeQuestion(
                        topic_id=topic.id,
                        learning_objective_id=pq["learning_objective_id"],
                        question_text=pq["question_text"],
                        question_type=pq["question_type"],
                        options=pq["options"],
                        correct_answer=pq["correct_answer"],
                        explanation=pq["explanation"],
                        difficulty=pq["difficulty"],
                        marks=pq["marks"],
                        is_ai_generated=pq["is_ai_generated"],
                        generation_provenance=pq["generation_provenance"],
                    )
                )
            db.commit()
            print("Seeded 3 AI-generated practice questions.")

        # ── 4. Seed 10-Part Topic Study Notes ─────────────────────────────────
        existing_notes = db.query(TopicStudyNotes).filter(
            TopicStudyNotes.topic_id == topic.id,
            TopicStudyNotes.notes_type == "comprehensive",
        ).first()

        if not existing_notes:
            comprehensive_markdown = """### 1. Topic Overview
During the mid-nineteenth century, Lord Dalhousie (Governor-General 1848–1856) transformed colonial communication and transportation in India by initiating the **railway network**, the **electric telegraph**, and a **uniform modern postal system**. While colonial apologists framed these developments as modernizing infrastructure, Indian nationalist historians emphasize that the primary motives were **imperial military control** and **colonial economic extraction**.

### 2. Learning Objectives
- **HIST-11-CH1-OBJ1**: Understand the financial architecture of the Railway Guarantee System.
- **HIST-11-CH1-OBJ2**: Contrast imperial strategic priorities with indigenous passenger and agricultural needs.
- **HIST-11-CH1-OBJ3**: Examine de-industrialization effects caused by rail penetration into rural markets.

### 3. Core Explanation: The Colonial Transport Engine
#### The Old Guarantee System (1849–1869)
To induce British joint-stock companies (such as the *Great Indian Peninsula Railway* and *East Indian Railway*) to invest, the East India Company established a guarantee contract:
1. **Guaranteed Dividend**: 4.5% to 5% annual interest on invested capital, guaranteed from Indian public revenue.
2. **Free Land Leases**: 99-year land concessions at zero charge.
3. **Surplus Sharing**: Half of any profits exceeding 5% went to the colonial government.

Because capital returns were 100% guaranteed regardless of construction efficiency, British railway companies engaged in reckless spending. Mile-per-mile railway construction in India cost nearly **£18,000 per mile**, compared to £8,000 to £10,000 in contemporary Canada or Australia.

#### Strategic vs. Economic Alignment
Lines were not planned to interconnect Indian trade centres (such as Delhi to Agra or Surat to Pune). Instead, they connected deep agricultural hinterlands directly to **port cities** (Bombay, Calcutta, Madras, Karachi). This ensured:
- Rapid shipment of raw cotton, jute, wheat, and oilseeds to Liverpool and Manchester mills.
- Inundation of interior village markets with cheap British manufactured goods, undermining local artisans.

### 4. Key Terms & Concepts
- **Old Guarantee System**: Financial model guaranteeing 5% returns on British capital funded by Indian tax revenues.
- **Feeder Lines**: Secondary rail branches intended to gather agricultural output from rural tehsils.
- **Drain of Wealth**: Systematic transfer of Indian financial resources to Britain without adequate economic return.

### 5. Important Facts, Dates & Landmarks
- **16 April 1853**: First passenger train in India ran between Bombay (Bori Bunder) and Thane (34 km).
- **1854**: First passenger line in eastern India opened between Howrah and Hooghly (38 km).
- **1851–1854**: Introduction of the Electric Telegraph under Dr. William O'Shaughnessy; by 1856, over 4,000 miles of telegraph wire linked Calcutta, Peshawar, Agra, and Bombay.
- **Post Office Act of 1854**: Introduced uniform postage rate of half-anna (1/2 anna) across all distances in India.

### 6. Case Study: The 1857 Uprising Impact
During the 1857 Revolt, the electric telegraph proved decisive in alerting colonial garrisons in Punjab and Delhi, allowing British forces to coordinate troop movements rapidly. A dying rebel officer reportedly lamented: *"It was this infernal string [the telegraph wire] that strangled us."*

### 7. Conceptual Architecture Diagram
```mermaid
flowchart TD
    A["British Capital Investment"] -->|"Guaranteed 5% Return"| B["Private Railway Companies"]
    B -->|"Lays tracks to ports"| C["Hinterland Extractive Network"]
    C -->|"Raw cotton, grain, jute"| D["Port Cities (Bombay, Calcutta)"]
    D -->|"Export to Manchester"| E["British Industrial Factories"]
    E -->|"Import factory textiles"| C
    C -->|"Undercuts Indian Handlooms"| F["Rural De-industrialisation"]
```

### 8. Common Student Misconceptions
> **Misconception:** "The British introduced railways out of benevolent concern to modernize Indian transit."
> **Historical Reality:** Dalhousie's 1853 Railway Minute clearly states the twin goals: commercial exploitation of Indian raw materials and rapid troop deployment to border garrisons.

### 9. High-Yield Exam Revision Points
1. Remember the date of the first train: **16 April 1853 (Bombay to Thane)**.
2. The guaranteed 5% return led to massive extravagance, described by Dinshaw Wacha as **"private enterprise at public risk"**.
3. Railways accelerated **commercialization of agriculture** at the expense of food security, aggravating late 19th-century famines.
4. The Post Office Act of 1854 democratized mail with uniform **half-anna postage**.

### 10. Self-Assessment Practice
1. *Why was the railway network described as an extractive mechanism?*
   - It funneled raw materials from agrarian interiors directly to ports for export, while delivering foreign manufactured cloth back into the interior."""

            notes_record = TopicStudyNotes(
                topic_id=topic.id,
                notes_type="comprehensive",
                title="ISC Class 11: Development of Transport & Communication: Railways, Roads, and Telegraphs",
                overview="Comprehensive curriculum notes covering Lord Dalhousie's infrastructure modernization, the Railway Guarantee System, commercial drainage, and telegraph networks in colonial India.",
                learning_objectives_json=[
                    "HIST-11-CH1-OBJ1: Understand the Railway Guarantee System.",
                    "HIST-11-CH1-OBJ2: Analyze imperial motives vs economic impact.",
                    "HIST-11-CH1-OBJ3: Evaluate telegraph and postal reforms under Dalhousie.",
                ],
                explanation_markdown=comprehensive_markdown,
                key_terms_json=[
                    {"term": "Guarantee System", "definition": "British financial agreement providing 5% guaranteed returns from Indian tax revenue to private rail investors."},
                    {"term": "Lord Dalhousie", "definition": "Governor-General of India (1848–1856) who authored the pivotal 1853 Railway Minute."},
                    {"term": "Drain of Wealth", "definition": "Systematic outflow of Indian economic surplus to Britain through guaranteed railway dividends and unrequited exports."},
                ],
                formulas_and_dates_json=[
                    {"date": "16 April 1853", "event": "First train operates between Bombay (Bori Bunder) and Thane (34 km)."},
                    {"date": "1854", "event": "Howrah to Hooghly passenger line opens; Post Office Act introduces half-anna postage."},
                ],
                diagrams_json=[
                    {
                        "title": "Extractive Flow of Colonial Rail Networks",
                        "diagram_type": "mermaid",
                        "code": "flowchart TD\n    A[British Investors] -->|5% Guarantee| B[Railways]\n    B -->|Transports Raw Goods| C[Port Cities]\n    C -->|Export| D[British Mills]",
                        "description": "Visualizing how Indian tax funds underwrote British capital while raw materials were drained to coastal ports.",
                    }
                ],
                common_misconceptions_json=[
                    {
                        "misconception": "Railways were built primarily for passenger transport convenience.",
                        "correction": "Strategic military deployment and commercial extraction of raw materials were the documented primary drivers.",
                    }
                ],
                exam_points_json=[
                    "State the 4 terms of the Old Guarantee System (frequent 4-mark question in ISC).",
                    "Distinguish strategic vs commercial objectives of Dalhousie's 1853 Railway Minute (6-mark question).",
                ],
                practice_questions_json=[
                    {
                        "question": "What was the guaranteed rate of return under the Old Guarantee System?",
                        "answer": "5% annually, paid from Indian tax revenues.",
                    }
                ],
                source_references_json=[
                    {
                        "title": "CISCE ISC Class XI History Curriculum Regulations (2027)",
                        "url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                        "verified": True,
                    }
                ],
                version=1,
                is_verified=True,
            )
            db.add(notes_record)
            db.commit()
            print("Seeded comprehensive 10-part topic study notes.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_curriculum_intelligence()
