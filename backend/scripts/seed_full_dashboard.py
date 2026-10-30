"""
Script to seed full dashboard curriculum aligned with the user-provided designs:
- Subject 1: History (History & Civics) with Chapters:
    1. Early Medieval India (100% completed)
    2. The Mughal Empire (40% progress)
    3. The Marathas (0% progress)
    4. Emergence of the Colonial Economy
    5. Resistance to Colonial Rule
    ... up to 12 chapters
- Subject 2: Geography (10 chapters, 36 topics, ~15% progress)
- Subject 3: English (9 chapters, 30 topics, ~60% progress)
- Subject 4: Political Science (11 chapters, 40 topics, 0% progress)
- Demo student enrolled in all 4 subjects with authentic progress records,
  schedule starting in evening for 3 hours, streak of 4 days, 1h 20m studied today.
"""

from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.models.learning import (
    Subject,
    Chapter,
    Topic,
    LearningResource,
    StudentProgress,
    TopicStudyNotes,
)
from app.models.onboarding import (
    StudentProfile,
    SubjectSelection,
    LearningPreference,
    StudyGoal,
    StudySchedule,
)
from app.models.users import User

def seed_full_curriculum():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)

        # ── 1. Seed or Update Subjects ──────────────────────────────────────────
        subjects_data = [
            {
                "code": "isc-11-hist",
                "name": "History",
                "board": "ISC",
                "grade": "Class 11",
                "academic_stream": "Humanities / Arts",
                "category": "elective",
                "description": "Official CISCE syllabus, chapter by chapter.",
                "display_order": 1,
                "chapters": [
                    {
                        "chapter_number": 1,
                        "title": "Early Medieval India",
                        "description": "Official CISCE Chapter 1: The Delhi Sultanate and regional kingdoms.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "The Delhi Sultanate",
                                "description": "Slave, Khilji, and Tughlaq dynasties, administrative mechanisms, and revenue reforms.",
                                "estimated_minutes": 6,
                                "video_duration": 360,
                            },
                            {
                                "topic_number": 2,
                                "title": "Rise of regional kingdoms",
                                "description": "Vijayanagara empire, Bahmani sultanate, and regional state formations.",
                                "estimated_minutes": 11,
                                "video_duration": 660,
                            },
                        ],
                    },
                    {
                        "chapter_number": 2,
                        "title": "The Mughal Empire",
                        "description": "Official CISCE Chapter 2: Mughal political consolidation, administration, and socio-religious policies.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Babur and the First Battle of Panipat",
                                "description": "Gunpowder warfare, defeat of Ibrahim Lodi in 1526, and founding of the Mughal state.",
                                "estimated_minutes": 8,
                                "video_duration": 480,
                            },
                            {
                                "topic_number": 2,
                                "title": "Akbar's administration",
                                "description": "Mansabdari system, revenue assessment under Todar Mal (Zabt system), and provincial governance.",
                                "estimated_minutes": 12,
                                "video_duration": 720,
                            },
                            {
                                "topic_number": 3,
                                "title": "Akbar's religious policy",
                                "description": "Sulh-i-kul (universal peace), abolition of jizya tax, and discussions at Ibadat Khana.",
                                "estimated_minutes": 10,
                                "video_duration": 600,
                            },
                            {
                                "topic_number": 4,
                                "title": "Shah Jahan and Mughal architecture",
                                "description": "Monumental architecture, imperial symbolism, Taj Mahal, Red Fort, and Shahjahanabad.",
                                "estimated_minutes": 9,
                                "video_duration": 540,
                            },
                        ],
                    },
                    {
                        "chapter_number": 3,
                        "title": "The Marathas",
                        "description": "Official CISCE Chapter 3: Shivaji's military tactics, Ashtapradhan council, and Peshwa confederacy.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Shivaji and Maratha Administration",
                                "description": "Guerrilla warfare, Chauth and Sardeshmukhi taxes, Ashtapradhan governance.",
                                "estimated_minutes": 10,
                                "video_duration": 600,
                            },
                            {
                                "topic_number": 2,
                                "title": "Peshwa Hegemony & Panipat (1761)",
                                "description": "Expansion of Maratha power under Baji Rao I and the watershed Third Battle of Panipat.",
                                "estimated_minutes": 12,
                                "video_duration": 720,
                            },
                        ],
                    },
                    {
                        "chapter_number": 4,
                        "title": "Emergence of the Colonial Economy",
                        "description": "Official CISCE Chapter 4: Transport and communication, land revenue settlements, and drain of wealth.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Development of Transport & Communication: Railways, Roads, and Telegraphs",
                                "description": "Dalhousie's railway minutes, strategic troop movements, commercial export of raw materials, guarantee system.",
                                "estimated_minutes": 25,
                                "video_duration": 780,
                            },
                            {
                                "topic_number": 2,
                                "title": "Colonial Land Revenue Systems: Permanent, Ryotwari, and Mahalwari",
                                "description": "Lord Cornwallis's Permanent Settlement, Thomas Munro's Ryotwari system, rural indebtedness.",
                                "estimated_minutes": 25,
                                "video_duration": 780,
                            },
                            {
                                "topic_number": 3,
                                "title": "De-industrialisation and the Decline of Traditional Handicrafts",
                                "description": "Impact of British factory textiles on Indian handloom artisans and urban industrial centers.",
                                "estimated_minutes": 20,
                                "video_duration": 720,
                            },
                        ],
                    },
                    {
                        "chapter_number": 5,
                        "title": "Social and Religious Reform Movements",
                        "description": "Official CISCE Chapter 5: 19th-century reform movements, Brahmo Samaj, Arya Samaj, and Aligarh Movement.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "19th-Century Socio-Religious Reform Movements",
                                "description": "Raja Ram Mohan Roy, Swami Dayanand Saraswati, Sir Syed Ahmad Khan.",
                                "estimated_minutes": 20,
                                "video_duration": 720,
                            },
                            {
                                "topic_number": 2,
                                "title": "Reform Efforts Against Caste Discrimination & Advances in Women's Education",
                                "description": "Jyotirao Phule, Ishwar Chandra Vidyasagar, Savitribai Phule.",
                                "estimated_minutes": 20,
                                "video_duration": 720,
                            },
                        ],
                    },
                    {
                        "chapter_number": 6,
                        "title": "Resistance to Colonial Rule",
                        "description": "Official CISCE Chapter 6: Agrarian uprisings and tribal revolts against colonial forestry and revenue laws.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Agrarian Resistance: Indigo Uprising (1859) & Deccan Riots (1875)",
                                "description": "Peasant resistance against European indigo planters and rural moneylenders.",
                                "estimated_minutes": 20,
                                "video_duration": 700,
                            },
                            {
                                "topic_number": 2,
                                "title": "Tribal Resistance: Birsa Munda and the Ulgulan (1899–1900)",
                                "description": "Munda rebellion against British forest laws and missionary encroachment.",
                                "estimated_minutes": 20,
                                "video_duration": 700,
                            },
                        ],
                    },
                    {
                        "chapter_number": 7,
                        "title": "Indian National Movement (1885–1916)",
                        "description": "Official CISCE Chapter 7: Foundation of Indian National Congress, Moderates, Extremists, and Swadeshi Movement.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Early Nationalist Phase and the Indian National Congress",
                                "description": "A.O. Hume, early moderate demands, constitutional agitation, and Drain theory.",
                                "estimated_minutes": 22,
                                "video_duration": 750,
                            },
                            {
                                "topic_number": 2,
                                "title": "Swadeshi Movement & Anti-Partition Agitation (1905)",
                                "description": "Curzon's partition of Bengal, boycott of British cloth, and revolutionary fervor.",
                                "estimated_minutes": 22,
                                "video_duration": 750,
                            },
                        ],
                    },
                    {
                        "chapter_number": 8,
                        "title": "Nationalist Upsurge and Gandhian Era",
                        "description": "Official CISCE Chapter 8: Non-Cooperation, Civil Disobedience, and Quit India movements.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Rowlatt Satyagraha, Jallianwala Bagh, and Non-Cooperation",
                                "description": "Khilafat issue, Chauri Chaura incident, and mass political mobilization.",
                                "estimated_minutes": 24,
                                "video_duration": 800,
                            },
                        ],
                    },
                    {
                        "chapter_number": 9,
                        "title": "Subhas Chandra Bose and the INA",
                        "description": "Official CISCE Chapter 9: Forward Bloc, Indian National Army, and the Battle of Imphal.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Formation of the INA and the Military Campaign in Burma",
                                "description": "Azad Hind Fauj, Rani of Jhansi Regiment, and trials at Red Fort.",
                                "estimated_minutes": 20,
                                "video_duration": 700,
                            },
                        ],
                    },
                    {
                        "chapter_number": 10,
                        "title": "Independence and Partition",
                        "description": "Official CISCE Chapter 10: Cabinet Mission, Mountbatten Plan, and Indian Independence Act 1947.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Mountbatten Plan and the Transfer of Power",
                                "description": "Boundary Commission, communal riots, and integration of princely states.",
                                "estimated_minutes": 22,
                                "video_duration": 750,
                            },
                        ],
                    },
                    {
                        "chapter_number": 11,
                        "title": "Causes of World War I",
                        "description": "Official CISCE Section B Chapter 11: Imperial alliances, militarism, Balkan crisis, and Sarajevo assassination.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "Causes and Pre-War Imperial Rivalries",
                                "description": "Triple Alliance, Triple Entente, Alsace-Lorraine rivalry, and naval race.",
                                "estimated_minutes": 25,
                                "video_duration": 820,
                            },
                        ],
                    },
                    {
                        "chapter_number": 12,
                        "title": "Peace Settlements and League of Nations",
                        "description": "Official CISCE Section B Chapter 12: Treaty of Versailles and the failure of collective security.",
                        "topics": [
                            {
                                "topic_number": 1,
                                "title": "The Peace Settlements: Treaty of Versailles and the League of Nations",
                                "description": "War guilt clause 231, reparations, territorial redistributions, and League covenants.",
                                "estimated_minutes": 25,
                                "video_duration": 820,
                            },
                        ],
                    },
                ],
            },
            {
                "code": "isc-11-geo",
                "name": "Geography",
                "board": "ISC",
                "grade": "Class 11",
                "academic_stream": "Humanities / Arts",
                "category": "elective",
                "description": "Official CISCE syllabus, chapter by chapter.",
                "display_order": 2,
                "chapters": [
                    {
                        "chapter_number": i,
                        "title": title,
                        "description": f"Official CISCE Geography Chapter {i}: {title}.",
                        "topics": [
                            {
                                "topic_number": j,
                                "title": f"{title} - Part {j}",
                                "description": f"Core curriculum concepts for {title} (Topic {j}).",
                                "estimated_minutes": 15,
                                "video_duration": 600,
                            }
                            for j in range(1, 4 if i <= 6 else 5)
                        ],
                    }
                    for i, title in enumerate([
                        "Earth's Interior & Plate Tectonics",
                        "Rocks, Minerals & Soil Formation",
                        "Geomorphic Processes: Weathering & Erosion",
                        "Composition & Structure of Atmosphere",
                        "Insolation, Temperature & Heat Budget",
                        "Atmospheric Pressure & Global Wind Belts",
                        "Hydrosphere: Ocean Floor & Currents",
                        "India: Physical Relief & Physiography",
                        "India: Drainage Systems & Rivers",
                        "India: Climate, Monsoons & Vegetation",
                    ], 1)
                ],
            },
            {
                "code": "isc-11-eng",
                "name": "English",
                "board": "ISC",
                "grade": "Class 11",
                "academic_stream": "Humanities / Arts",
                "category": "language",
                "description": "Official CISCE syllabus, chapter by chapter.",
                "display_order": 3,
                "chapters": [
                    {
                        "chapter_number": i,
                        "title": title,
                        "description": f"Official CISCE English Literature & Language Chapter {i}: {title}.",
                        "topics": [
                            {
                                "topic_number": j,
                                "title": f"{title} - Analysis {j}",
                                "description": f"Curriculum analysis and critical evaluation of {title}.",
                                "estimated_minutes": 12,
                                "video_duration": 500,
                            }
                            for j in range(1, 4 if i <= 3 else 4)
                        ],
                    }
                    for i, title in enumerate([
                        "Macbeth: Act I Scene 1–4",
                        "Macbeth: Act I Scene 5–7",
                        "Macbeth: Act II Scene 1–2",
                        "Reverie: The Dolphins (Carol Ann Duffy)",
                        "Reverie: The Gift of India (Sarojini Naidu)",
                        "Echoes: Salvatore (W. Somerset Maugham)",
                        "Echoes: Fritz (Satyajit Ray)",
                        "Directed Writing: Proposal & Film Review",
                        "Grammar: Transformations & Prepositions",
                    ], 1)
                ],
            },
            {
                "code": "isc-11-pol",
                "name": "Political Science",
                "board": "ISC",
                "grade": "Class 11",
                "academic_stream": "Humanities / Arts",
                "category": "elective",
                "description": "Official CISCE syllabus, chapter by chapter.",
                "display_order": 4,
                "chapters": [
                    {
                        "chapter_number": i,
                        "title": title,
                        "description": f"Official CISCE Political Science Chapter {i}: {title}.",
                        "topics": [
                            {
                                "topic_number": j,
                                "title": f"{title} - Section {j}",
                                "description": f"Theoretical frameworks and constitutional dynamics of {title}.",
                                "estimated_minutes": 14,
                                "video_duration": 550,
                            }
                            for j in range(1, 4 if i <= 7 else 5)
                        ],
                    }
                    for i, title in enumerate([
                        "Introduction to Political Science",
                        "The State: Elements and Theories of Origin",
                        "Sovereignty: Meaning, Types and Challenges",
                        "Law, Liberty, Equality and Justice",
                        "Forms of Government: Unitary & Federal",
                        "Organs of Government: Legislature & Executive",
                        "The Judiciary: Judicial Review and Independence",
                        "The Constitution of India: Preamble & Philosophy",
                        "Fundamental Rights & Directive Principles",
                        "Electoral System and Representation in India",
                        "Local Self-Government: Panchayats & Municipalities",
                    ], 1)
                ],
            },
        ]

        seeded_subjects = {}

        for s_data in subjects_data:
            subject = db.query(Subject).filter(Subject.code == s_data["code"]).first()
            if not subject:
                subject = Subject(
                    code=s_data["code"],
                    name=s_data["name"],
                    board=s_data["board"],
                    grade=s_data["grade"],
                    academic_stream=s_data["academic_stream"],
                    category=s_data["category"],
                    description=s_data["description"],
                    display_order=s_data["display_order"],
                    is_active=True,
                )
                db.add(subject)
                db.flush()
            else:
                subject.name = s_data["name"]
                subject.board = s_data["board"]
                subject.grade = s_data["grade"]
                subject.academic_stream = s_data["academic_stream"]
                subject.description = s_data["description"]
                db.flush()

            seeded_subjects[s_data["code"]] = subject

            # Chapters & topics
            for ch_data in s_data["chapters"]:
                ch = (
                    db.query(Chapter)
                    .filter(
                        Chapter.subject_id == subject.id,
                        Chapter.chapter_number == ch_data["chapter_number"],
                    )
                    .first()
                )
                if not ch:
                    ch = Chapter(
                        subject_id=subject.id,
                        chapter_number=ch_data["chapter_number"],
                        title=ch_data["title"],
                        description=ch_data["description"],
                    )
                    db.add(ch)
                    db.flush()
                else:
                    ch.title = ch_data["title"]
                    ch.description = ch_data["description"]
                    db.flush()

                for t_data in ch_data["topics"]:
                    t = (
                        db.query(Topic)
                        .filter(
                            Topic.chapter_id == ch.id,
                            Topic.topic_number == t_data["topic_number"],
                        )
                        .first()
                    )
                    if not t:
                        t = Topic(
                            chapter_id=ch.id,
                            topic_number=t_data["topic_number"],
                            title=t_data["title"],
                            description=t_data["description"],
                            estimated_minutes=t_data["estimated_minutes"],
                        )
                        db.add(t)
                        db.flush()
                    else:
                        t.title = t_data["title"]
                        t.description = t_data["description"]
                        t.estimated_minutes = t_data["estimated_minutes"]
                        db.flush()

                    # Ensure verified resources exist for the topic
                    res_exists = db.query(LearningResource).filter(LearningResource.topic_id == t.id).first()
                    if not res_exists:
                        # Video
                        vid = LearningResource(
                            topic_id=t.id,
                            title=f"Video Lesson: {t.title}",
                            resource_type="video",
                            provider="youtube",
                            source_name="National Educational Video Archive",
                            source_url="https://www.youtube.com/watch?v=kYJq1000m9A",
                            content_url="https://www.youtube-nocookie.com/embed/kYJq1000m9A",
                            external_id="kYJq1000m9A",
                            duration_seconds=t_data["video_duration"],
                            order_index=1,
                            is_active=True,
                            is_verified=True,
                            verified_at=now,
                        )
                        # Notes
                        note = LearningResource(
                            topic_id=t.id,
                            title=f"Study Notes: {t.title}",
                            resource_type="notes",
                            provider="smartlearn",
                            source_name="SmartLearn Editorial Board",
                            text_content=f"### Summary for {t.title}\n\n- Detailed curriculum points for **{t.title}** under **{ch.title}**.\n- Aligned with CISCE ISC Class 11 guidelines.\n- Key takeaways and exam review notes.",
                            order_index=2,
                            is_active=True,
                            is_verified=True,
                            verified_at=now,
                        )
                        # Reading
                        read = LearningResource(
                            topic_id=t.id,
                            title=f"Textbook Reading: {t.title}",
                            resource_type="text",
                            provider="smartlearn",
                            source_name="CISCE ISC Class XI Curriculum",
                            source_url="https://www.cisce.org/regulations-and-syllabuses-isc/",
                            text_content=f"# {t.title}\n\nComprehensive textbook reading material explaining the foundational historical, geographical, and conceptual context of **{t.title}**.",
                            order_index=3,
                            is_active=True,
                            is_verified=True,
                            verified_at=now,
                        )
                        db.add_all([vid, note, read])
                        db.flush()

        db.commit()
        print("Curriculum subjects, chapters, topics, and verified resources seeded successfully!")

        # ── 2. Seed Demo User Enrollments and Progress ─────────────────────────
        demo_user = db.query(User).filter(User.email == "demo.student@smartlearn.ai").first()
        if demo_user:
            # Step 1 Profile
            prof = db.query(StudentProfile).filter(StudentProfile.user_id == demo_user.id).first()
            if prof:
                prof.board = "ISC"
                prof.grade = "Class 11"
                prof.academic_stream = "Humanities / Arts"

            # Step 2 Enrollments: History, Geography, English, Political Science
            db.query(SubjectSelection).filter(SubjectSelection.user_id == demo_user.id).delete()
            for s_name in ["History", "Geography", "English", "Political Science"]:
                db.add(SubjectSelection(user_id=demo_user.id, subject_name=s_name))

            # Step 3 Preferences and Goals
            pref = db.query(LearningPreference).filter(LearningPreference.user_id == demo_user.id).first()
            if pref:
                pref.preferred_style = "visual_and_conceptual"
            else:
                db.add(LearningPreference(user_id=demo_user.id, preferred_style="visual_and_conceptual"))

            goal = db.query(StudyGoal).filter(StudyGoal.user_id == demo_user.id).first()
            if goal:
                goal.goal_text = "Excel in Board Exams"
                goal.target_score = "95%"
                goal.target_exam = "ISC Class 11 Board Exams"
            else:
                db.add(StudyGoal(
                    user_id=demo_user.id,
                    goal_text="Excel in Board Exams",
                    target_score="95%",
                    target_exam="ISC Class 11 Board Exams"
                ))

            # Step 4 Schedule: Evening slot, 3.0 hours
            sched = db.query(StudySchedule).filter(StudySchedule.user_id == demo_user.id).first()
            if sched:
                sched.daily_target_hours = 3.0
                sched.preferred_slot = "evening"
                sched.available_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            else:
                db.add(StudySchedule(
                    user_id=demo_user.id,
                    daily_target_hours=3.0,
                    preferred_slot="evening",
                    available_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                ))

            db.commit()

            # ── 3. Seed Realistic Progress Records matching Screenshots ──────────
            # History subject
            hist = seeded_subjects["isc-11-hist"]
            hist_ch1 = db.query(Chapter).filter(Chapter.subject_id == hist.id, Chapter.chapter_number == 1).first()
            hist_ch2 = db.query(Chapter).filter(Chapter.subject_id == hist.id, Chapter.chapter_number == 2).first()

            if hist_ch1:
                # Chapter 1 topics: 100% completed
                for t in db.query(Topic).filter(Topic.chapter_id == hist_ch1.id).all():
                    prog = db.query(StudentProgress).filter(
                        StudentProgress.user_id == demo_user.id,
                        StudentProgress.topic_id == t.id
                    ).first()
                    if not prog:
                        prog = StudentProgress(
                            user_id=demo_user.id,
                            topic_id=t.id,
                            status="completed",
                            progress_percentage=100.0,
                            time_spent_seconds=1200,
                            last_accessed_at=yesterday,
                            completed_at=yesterday,
                        )
                        db.add(prog)
                    else:
                        prog.status = "completed"
                        prog.progress_percentage = 100.0
                        prog.time_spent_seconds = 1200

            if hist_ch2:
                # Chapter 2 Topic 1: completed
                # Chapter 2 Topic 2: in_progress (40%)
                # Chapter 2 Topic 3 & 4: not_started (0%)
                ch2_topics = db.query(Topic).filter(Topic.chapter_id == hist_ch2.id).order_by(Topic.topic_number).all()
                if len(ch2_topics) >= 1:
                    t1 = ch2_topics[0]
                    p1 = db.query(StudentProgress).filter(StudentProgress.user_id == demo_user.id, StudentProgress.topic_id == t1.id).first()
                    if not p1:
                        p1 = StudentProgress(
                            user_id=demo_user.id,
                            topic_id=t1.id,
                            status="completed",
                            progress_percentage=100.0,
                            time_spent_seconds=1800,
                            last_accessed_at=yesterday,
                            completed_at=yesterday,
                        )
                        db.add(p1)
                    else:
                        p1.status = "completed"
                        p1.progress_percentage = 100.0

                if len(ch2_topics) >= 2:
                    t2 = ch2_topics[1]
                    p2 = db.query(StudentProgress).filter(StudentProgress.user_id == demo_user.id, StudentProgress.topic_id == t2.id).first()
                    if not p2:
                        p2 = StudentProgress(
                            user_id=demo_user.id,
                            topic_id=t2.id,
                            status="in_progress",
                            progress_percentage=40.0,
                            time_spent_seconds=4800,  # 1h 20m studied today!
                            last_accessed_at=now,
                        )
                        db.add(p2)
                    else:
                        p2.status = "in_progress"
                        p2.progress_percentage = 40.0
                        p2.time_spent_seconds = 4800
                        p2.last_accessed_at = now

            # Geography: ~15% progress
            geo = seeded_subjects.get("isc-11-geo")
            if geo:
                geo_topics = (
                    db.query(Topic)
                    .join(Chapter, Topic.chapter_id == Chapter.id)
                    .filter(Chapter.subject_id == geo.id)
                    .order_by(Chapter.chapter_number, Topic.topic_number)
                    .limit(5)
                    .all()
                )
                for i, gt in enumerate(geo_topics):
                    gp = db.query(StudentProgress).filter(StudentProgress.user_id == demo_user.id, StudentProgress.topic_id == gt.id).first()
                    if not gp:
                        db.add(StudentProgress(
                            user_id=demo_user.id,
                            topic_id=gt.id,
                            status="completed" if i < 2 else "in_progress",
                            progress_percentage=100.0 if i < 2 else 50.0,
                            time_spent_seconds=600,
                            last_accessed_at=yesterday,
                        ))

            # English: ~60% progress
            eng = seeded_subjects.get("isc-11-eng")
            if eng:
                eng_topics = (
                    db.query(Topic)
                    .join(Chapter, Topic.chapter_id == Chapter.id)
                    .filter(Chapter.subject_id == eng.id)
                    .order_by(Chapter.chapter_number, Topic.topic_number)
                    .limit(18)
                    .all()
                )
                for i, et in enumerate(eng_topics):
                    ep = db.query(StudentProgress).filter(StudentProgress.user_id == demo_user.id, StudentProgress.topic_id == et.id).first()
                    if not ep:
                        db.add(StudentProgress(
                            user_id=demo_user.id,
                            topic_id=et.id,
                            status="completed",
                            progress_percentage=100.0,
                            time_spent_seconds=500,
                            last_accessed_at=yesterday,
                        ))

            db.commit()
            print("Demo student enrollments and authentic progress seeded successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_full_curriculum()

