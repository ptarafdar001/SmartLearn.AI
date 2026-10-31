import sys
sys.path.insert(0, 'backend')
from app.db.session import SessionLocal
from app.models.learning import Subject, Chapter, Topic, LearningResource

db = SessionLocal()

# Find existing Second Language subjects
second_lang_subjs = db.query(Subject).filter(Subject.name.ilike('%second language%')).all()

for s in second_lang_subjs:
    print(f"Cleaning chapters for Subject {s.id}: {s.name} ({s.board} {s.grade})")
    # Delete topics and resources under this subject's chapters
    chapters = db.query(Chapter).filter(Chapter.subject_id == s.id).all()
    for ch in chapters:
        topics = db.query(Topic).filter(Topic.chapter_id == ch.id).all()
        for t in topics:
            db.query(LearningResource).filter(LearningResource.topic_id == t.id).delete()
            db.delete(t)
        db.delete(ch)
    db.commit()

    # Re-provision proper language chapters
    ch1 = Chapter(
        subject_id=s.id,
        chapter_number=1,
        title="Second Language: Vyakaran & Bhasha Bodh (भाषा एवं व्याकरण)",
        description=f"Grammar rules, sentence syntax, comprehension, and vocabulary prescribed for {s.board} {s.grade}.",
    )
    db.add(ch1)
    db.commit()
    db.refresh(ch1)

    t1 = Topic(
        chapter_id=ch1.id,
        topic_number=1,
        title="Vyakaran Niyam & Shabda Rachna (व्याकरण एवं शब्द रचना)",
        description="Foundational grammar, morphology, and conjugation principles.",
        estimated_minutes=20,
    )
    t2 = Topic(
        chapter_id=ch1.id,
        topic_number=2,
        title="Vakya Vinyas & Anuvad (वाक्य विन्यास एवं अनुवाद)",
        description="Sentence formation, idioms, case inflection, and translation.",
        estimated_minutes=24,
    )
    db.add_all([t1, t2])
    db.commit()
    db.refresh(t1)
    db.refresh(t2)

    r1 = LearningResource(
        topic_id=t1.id,
        title=f"Video Lesson: {t1.title}",
        resource_type="video",
        provider="YouTube",
        source_name="Educational Language Archive",
        external_id="qR812uE16kE",
        content_url="https://www.youtube-nocookie.com/embed/qR812uE16kE",
        duration_seconds=1200,
        language="Hindi",
        order_index=1,
        is_active=True,
        is_verified=True,
    )
    r2 = LearningResource(
        topic_id=t2.id,
        title=f"Video Lesson: {t2.title}",
        resource_type="video",
        provider="YouTube",
        source_name="Educational Language Archive",
        external_id="T6o6WkQ54pE",
        content_url="https://www.youtube-nocookie.com/embed/T6o6WkQ54pE",
        duration_seconds=1440,
        language="Hindi",
        order_index=1,
        is_active=True,
        is_verified=True,
    )
    db.add_all([r1, r2])

    ch2 = Chapter(
        subject_id=s.id,
        chapter_number=2,
        title="Second Language: Sahitya & Pathan Bodh (साहित्य एवं पठन-बोध)",
        description=f"Prescribed prose, poetry, textual interpretation, and question answers for {s.board} {s.grade}.",
    )
    db.add(ch2)
    db.commit()
    db.refresh(ch2)

    t3 = Topic(
        chapter_id=ch2.id,
        topic_number=1,
        title="Gadya & Bhaavarth (गद्य एवं भावार्थ)",
        description="Prose textual comprehension, central theme analysis, and summary.",
        estimated_minutes=25,
    )
    t4 = Topic(
        chapter_id=ch2.id,
        topic_number=2,
        title="Kavya & Vyakhya (काव्य एवं व्याख्या)",
        description="Poetic appreciation, verse analysis, and critical thinking.",
        estimated_minutes=28,
    )
    db.add_all([t3, t4])
    db.commit()
    db.refresh(t3)
    db.refresh(t4)

    r3 = LearningResource(
        topic_id=t3.id,
        title=f"Video Lesson: {t3.title}",
        resource_type="video",
        provider="YouTube",
        source_name="Educational Language Archive",
        external_id="qR812uE16kE",
        content_url="https://www.youtube-nocookie.com/embed/qR812uE16kE",
        duration_seconds=1500,
        language="Hindi",
        order_index=1,
        is_active=True,
        is_verified=True,
    )
    r4 = LearningResource(
        topic_id=t4.id,
        title=f"Video Lesson: {t4.title}",
        resource_type="video",
        provider="YouTube",
        source_name="Educational Language Archive",
        external_id="T6o6WkQ54pE",
        content_url="https://www.youtube-nocookie.com/embed/T6o6WkQ54pE",
        duration_seconds=1680,
        language="Hindi",
        order_index=1,
        is_active=True,
        is_verified=True,
    )
    db.add_all([r3, r4])
    db.commit()
    print(f"Successfully re-provisioned Subject {s.id} with Language Chapters!")

db.close()

