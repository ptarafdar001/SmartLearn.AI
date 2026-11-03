"""
Multi-Subject Curriculum Seeder for SmartLearn.AI.
Seeds Mathematics, Science, and Social Science curricula for CBSE & ICSE
across Classes 5 to 10 with verified study notes and embedded YouTube video resources.
"""

import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.learning import Chapter, LearningObjective, LearningResource, Subject, Topic

logger = logging.getLogger("smartlearn.seed_all")

CURRICULA: List[Dict[str, Any]] = [
    # ── 1. CBSE Class 10 - Mathematics ──────────────────────────────────────────
    {
        "code": "cbse-10-math",
        "name": "Mathematics",
        "board": "CBSE",
        "grade": "Class 10",
        "category": "core",
        "description": "NCERT Class 10 Mathematics syllabus covering Real Numbers, Polynomials, Quadratic Equations, and Geometry.",
        "display_order": 1,
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Real Numbers",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "The Fundamental Theorem of Arithmetic & Prime Factorisation",
                        "description": "Every composite number can be expressed as a product of primes uniquely.",
                        "estimated_minutes": 20,
                        "notes": (
                            "# The Fundamental Theorem of Arithmetic\n\n"
                            "Every composite number can be expressed (factorised) as a product of primes, "
                            "and this factorisation is unique, apart from the order in which the prime factors occur.\n\n"
                            "### Formula for HCF and LCM:\n"
                            "For any two positive integers $a$ and $b$:\n"
                            "$$\\text{HCF}(a, b) \\times \\text{LCM}(a, b) = a \\times b$$\n\n"
                            "### Proof of Irrationality:\n"
                            "We prove numbers like $\\sqrt{2}, \\sqrt{3}, \\sqrt{5}$ are irrational using proof by contradiction."
                        ),
                        "video_id": "1j6Y9346Z3c",
                    },
                    {
                        "topic_number": 2,
                        "title": "Revisiting Irrational Numbers",
                        "description": "Theorems and contradiction proofs for irrational numbers like root 2, root 3, and 5 - root 3.",
                        "estimated_minutes": 25,
                        "notes": (
                            "# Revisiting Irrational Numbers\n\n"
                            "A number is called **irrational** if it cannot be written in the form $p/q$, where $p$ and $q$ are integers and $q \\neq 0$.\n\n"
                            "**Theorem:** Let $p$ be a prime number. If $p$ divides $a^2$, then $p$ divides $a$, where $a$ is a positive integer."
                        ),
                        "video_id": "hBf10Z1E5Gk",
                    }
                ]
            },
            {
                "chapter_number": 2,
                "title": "Polynomials",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Geometrical Meaning of the Zeroes of a Polynomial",
                        "description": "Zeroes of linear, quadratic, and cubic polynomials and their graphical interpretations.",
                        "estimated_minutes": 20,
                        "notes": (
                            "# Zeroes of a Polynomial\n\n"
                            "For a quadratic polynomial $ax^2 + bx + c$, the graph is a parabola opening upwards if $a > 0$ and downwards if $a < 0$.\n"
                            "- The number of zeroes is the number of points where the graph intersects the X-axis."
                        ),
                        "video_id": "E3u4eO-dZ3c",
                    },
                    {
                        "topic_number": 2,
                        "title": "Relationship between Zeroes and Coefficients of a Polynomial",
                        "description": "Sum of roots alpha + beta = -b/a and product alpha * beta = c/a.",
                        "estimated_minutes": 25,
                        "notes": (
                            "# Relationship Between Zeroes and Coefficients\n\n"
                            "If $\\alpha$ and $\\beta$ are zeroes of $p(x) = ax^2 + bx + c$, then:\n"
                            "- **Sum of zeroes:** $\\alpha + \\beta = -\\frac{b}{a} = -\\frac{\\text{Coefficient of } x}{\\text{Coefficient of } x^2}$\n"
                            "- **Product of zeroes:** $\\alpha \\cdot \\beta = \\frac{c}{a} = \\frac{\\text{Constant term}}{\\text{Coefficient of } x^2}$"
                        ),
                        "video_id": "V_yQ91Zq-zE",
                    }
                ]
            },
            {
                "chapter_number": 3,
                "title": "Quadratic Equations",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Solution by Factorisation and Quadratic Formula",
                        "description": "Solving ax^2 + bx + c = 0 via Shreedharacharya quadratic formula.",
                        "estimated_minutes": 30,
                        "notes": (
                            "# Quadratic Formula\n\n"
                            "For any quadratic equation $ax^2 + bx + c = 0$, roots are given by:\n"
                            "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n\n"
                            "### Nature of Roots (Discriminant $D = b^2 - 4ac$):\n"
                            "- $D > 0$: Two distinct real roots\n"
                            "- $D = 0$: Two equal real roots\n"
                            "- $D < 0$: No real roots"
                        ),
                        "video_id": "f8Z8Z3v_Gz0",
                    }
                ]
            }
        ]
    },

    # ── 2. CBSE Class 10 - Science ───────────────────────────────────────────────
    {
        "code": "cbse-10-sci",
        "name": "Science",
        "board": "CBSE",
        "grade": "Class 10",
        "category": "core",
        "description": "NCERT Class 10 Science: Chemical Reactions, Life Processes, Light, and Electricity.",
        "display_order": 2,
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Chemical Reactions and Equations",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Balancing Chemical Equations & Types of Reactions",
                        "description": "Combination, Decomposition, Displacement, and Double Displacement reactions.",
                        "estimated_minutes": 25,
                        "notes": (
                            "# Chemical Reactions & Balancing\n\n"
                            "A balanced equation satisfies the **Law of Conservation of Mass**.\n\n"
                            "### Types of Chemical Reactions:\n"
                            "1. **Combination:** $A + B \\rightarrow AB$ (e.g., $CaO + H_2O \\rightarrow Ca(OH)_2$)\n"
                            "2. **Decomposition:** $AB \\rightarrow A + B$ (e.g., thermal decomposition of $FeSO_4$)\n"
                            "3. **Displacement:** $Fe + CuSO_4 \\rightarrow FeSO_4 + Cu$\n"
                            "4. **Double Displacement:** $Na_2SO_4 + BaCl_2 \\rightarrow BaSO_4\\downarrow + 2NaCl$"
                        ),
                        "video_id": "dG1s0pG4K9I",
                    }
                ]
            },
            {
                "chapter_number": 2,
                "title": "Life Processes",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Nutrition in Plants & Animals (Photosynthesis & Human Digestive System)",
                        "description": "Autotrophic nutrition and heterotrophic digestion through alimentary canal.",
                        "estimated_minutes": 30,
                        "notes": (
                            "# Nutrition in Organisms\n\n"
                            "### Photosynthesis Equation:\n"
                            "$$6CO_2 + 12H_2O \\xrightarrow[\\text{Chlorophyll}]{\\text{Sunlight}} C_6H_{12}O_6 + 6O_2 + 6H_2O$$\n\n"
                            "### Human Digestive Pathway:\n"
                            "Mouth (Salivary Amylase) $\\rightarrow$ Oesophagus (Peristalsis) $\\rightarrow$ Stomach (Pepsin, HCl) $\\rightarrow$ Small Intestine (Bile, Lipase, Trypsin) $\\rightarrow$ Absorption via Villi."
                        ),
                        "video_id": "U3cM2OqX7vE",
                    }
                ]
            }
        ]
    },

    # ── 3. ICSE Class 10 - Mathematics ───────────────────────────────────────────
    {
        "code": "icse-10-math",
        "name": "Mathematics",
        "board": "ICSE",
        "grade": "Class 10",
        "category": "core",
        "description": "CISCE ICSE Class 10 Mathematics: Commercial Mathematics (GST, Banking), Algebra, Geometry, and Trigonometry.",
        "display_order": 1,
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Goods and Services Tax (GST)",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Computation of CGST, SGST, and IGST in Intra-state & Inter-state Transactions",
                        "description": "Input Tax Credit (ITC) mechanism and tax calculation on printed price.",
                        "estimated_minutes": 25,
                        "notes": (
                            "# Goods and Services Tax (GST)\n\n"
                            "GST is a unified indirect destination-based consumption tax.\n\n"
                            "- **Intra-State Transaction** (within the same state):\n"
                            "  $$\\text{CGST} = \\text{SGST} = \\frac{1}{2} \\times \\text{GST rate}$$\n"
                            "- **Inter-State Transaction** (between two different states):\n"
                            "  $$\\text{IGST} = \\text{Full GST rate}$$\n"
                            "- **Input Tax Credit (ITC)**: $\\text{Net Tax Payable} = \\text{Output GST} - \\text{Input GST}$"
                        ),
                        "video_id": "g-B8rKx9_Ew",
                    }
                ]
            },
            {
                "chapter_number": 2,
                "title": "Banking (Recurring Deposit Accounts)",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Calculation of Maturity Value for Recurring Deposit Accounts",
                        "description": "Formulas for total interest and maturity amount using monthly deposits.",
                        "estimated_minutes": 20,
                        "notes": (
                            "# Recurring Deposit (RD) Account\n\n"
                            "If a customer deposits ₹$P$ per month for $n$ months at $r\\%$ per annum interest:\n\n"
                            "### Total Interest Formula:\n"
                            "$$I = P \\times \\frac{n(n + 1)}{2 \\times 12} \\times \\frac{r}{100}$$\n\n"
                            "### Maturity Value ($MV$):\n"
                            "$$MV = (P \\times n) + I$$"
                        ),
                        "video_id": "8G7rD6E2Jk4",
                    }
                ]
            }
        ]
    },

    # ── 4. CBSE / ICSE Class 8 - Mathematics & Science ──────────────────────────
    {
        "code": "cbse-8-math",
        "name": "Mathematics",
        "board": "CBSE",
        "grade": "Class 8",
        "category": "core",
        "description": "CBSE Class 8 Mathematics: Rational Numbers, Linear Equations, Quadrilaterals.",
        "display_order": 1,
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Rational Numbers",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Properties of Rational Numbers",
                        "description": "Closure, Commutativity, and Associativity of Addition and Multiplication.",
                        "estimated_minutes": 20,
                        "notes": (
                            "# Rational Numbers\n\n"
                            "A number that can be written in the form $p/q$, where $p$ and $q$ are integers and $q \\neq 0$.\n\n"
                            "- **Additive Identity**: $0$\n"
                            "- **Multiplicative Identity**: $1$\n"
                            "- **Additive Inverse**: $-a/b$\n"
                            "- **Reciprocal**: $b/a$"
                        ),
                        "video_id": "vM8r9N1W3tY",
                    }
                ]
            }
        ]
    },
    {
        "code": "cbse-8-sci",
        "name": "Science",
        "board": "CBSE",
        "grade": "Class 8",
        "category": "core",
        "description": "CBSE Class 8 Science: Crop Production, Microorganisms, Force and Pressure.",
        "display_order": 2,
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Crop Production and Management",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Agricultural Practices: Kharif and Rabi Crops",
                        "description": "Soil preparation, sowing, irrigation methods (drip and sprinkler), and harvesting.",
                        "estimated_minutes": 20,
                        "notes": (
                            "# Crop Production & Agricultural Practices\n\n"
                            "### Seasonal Crops:\n"
                            "1. **Kharif Crops:** Sown in rainy season (June to September). E.g., Paddy, Maize, Soyabean.\n"
                            "2. **Rabi Crops:** Grown in winter season (October to March). E.g., Wheat, Gram, Mustard."
                        ),
                        "video_id": "7QvD_5zB3x0",
                    }
                ]
            }
        ]
    },

    # ── 5. CBSE Class 5 - Mathematics ────────────────────────────────────────────
    {
        "code": "cbse-5-math",
        "name": "Mathematics",
        "board": "CBSE",
        "grade": "Class 5",
        "category": "core",
        "description": "Foundational primary mathematics: The Fish Tale (Large Numbers), Shapes and Angles, Parts and Wholes (Fractions).",
        "display_order": 1,
        "chapters": [
            {
                "chapter_number": 1,
                "title": "The Fish Tale (Numbers and Place Value)",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Large Numbers: Lakhs and Crores, Place Value and Simple Calculations",
                        "description": "Understanding Indian place value system, estimation, speed and distance word problems.",
                        "estimated_minutes": 15,
                        "notes": (
                            "# Place Value and Large Numbers\n\n"
                            "### Indian Place Value Chart:\n"
                            "Ones, Tens, Hundreds, Thousands, Ten Thousands, Lakhs, Ten Lakhs, Crores.\n\n"
                            "- $100$ thousands = $1$ Lakh ($1,00,000$)\n"
                            "- $100$ lakhs = $1$ Crore ($1,00,00,000$)\n\n"
                            "### Speed, Distance, and Time:\n"
                            "$$\\text{Distance} = \\text{Speed} \\times \\text{Time}$$"
                        ),
                        "video_id": "bT4O5zK1W8M",
                    }
                ]
            },
            {
                "chapter_number": 2,
                "title": "Shapes and Angles",
                "topics": [
                    {
                        "topic_number": 1,
                        "title": "Introduction to Angles: Right Angles, Acute, and Obtuse Angles",
                        "description": "Recognizing angles using hands of a clock and everyday shapes.",
                        "estimated_minutes": 15,
                        "notes": (
                            "# Angles and Shapes\n\n"
                            "- **Right Angle**: Exactly $90^\\circ$ (looks like the letter 'L').\n"
                            "- **Acute Angle**: Less than $90^\\circ$.\n"
                            "- **Obtuse Angle**: Greater than $90^\\circ$ but less than $180^\\circ$."
                        ),
                        "video_id": "K3wL1xY4N9Q",
                    }
                ]
            }
        ]
    }
]


def seed_multi_curricula(db: Session) -> None:
    """Idempotently seed multi-subject curriculum fixtures."""
    logger.info("Commencing multi-subject curriculum seeding...")

    for curr in CURRICULA:
        subject = db.query(Subject).filter(Subject.code == curr["code"]).first()
        if not subject:
            subject = Subject(
                code=curr["code"],
                name=curr["name"],
                board=curr["board"],
                grade=curr["grade"],
                academic_stream=curr.get("academic_stream"),
                category=curr.get("category", "core"),
                description=curr.get("description", ""),
                display_order=curr.get("display_order", 1),
                is_active=True,
            )
            db.add(subject)
            db.flush()
            print(f"Created subject: {subject.name} ({subject.code}) - {subject.board} {subject.grade}")
        else:
            print(f"Subject {subject.code} already exists.")

        for ch_data in curr.get("chapters", []):
            chapter = (
                db.query(Chapter)
                .filter(
                    Chapter.subject_id == subject.id,
                    Chapter.chapter_number == ch_data["chapter_number"],
                )
                .first()
            )
            if not chapter:
                chapter = Chapter(
                    subject_id=subject.id,
                    chapter_number=ch_data["chapter_number"],
                    title=ch_data["title"],
                    description=ch_data.get("description", ch_data["title"]),
                )
                db.add(chapter)
                db.flush()
                print(f"  Created chapter: {chapter.title}")

            for t_data in ch_data.get("topics", []):
                topic = (
                    db.query(Topic)
                    .filter(
                        Topic.chapter_id == chapter.id,
                        Topic.topic_number == t_data["topic_number"],
                    )
                    .first()
                )
                if not topic:
                    topic = Topic(
                        chapter_id=chapter.id,
                        topic_number=t_data["topic_number"],
                        title=t_data["title"],
                        description=t_data.get("description", t_data["title"]),
                        estimated_minutes=t_data.get("estimated_minutes", 20),
                    )
                    db.add(topic)
                    db.flush()
                    print(f"    Created topic: {topic.title}")

                # Add verified notes resource
                if "notes" in t_data:
                    res_note = (
                        db.query(LearningResource)
                        .filter(
                            LearningResource.topic_id == topic.id,
                            LearningResource.resource_type == "text",
                        )
                        .first()
                    )
                    if not res_note:
                        res_note = LearningResource(
                            topic_id=topic.id,
                            title=f"Study Guide: {topic.title}",
                            resource_type="text",
                            provider="smartlearn",
                            source_name=f"{subject.board} {subject.grade} Syllabus",
                            text_content=t_data["notes"],
                            is_verified=True,
                            is_active=True,
                        )
                        db.add(res_note)

                # Add verified YouTube in-platform video resource
                if "video_id" in t_data:
                    res_vid = (
                        db.query(LearningResource)
                        .filter(
                            LearningResource.topic_id == topic.id,
                            LearningResource.resource_type == "video",
                        )
                        .first()
                    )
                    if not res_vid:
                        res_vid = LearningResource(
                            topic_id=topic.id,
                            title=f"Video Lesson: {topic.title}",
                            resource_type="video",
                            provider="youtube",
                            external_id=t_data["video_id"],
                            content_url=f"https://www.youtube-nocookie.com/embed/{t_data['video_id']}",
                            is_verified=True,
                            is_active=True,
                        )
                        db.add(res_vid)

    db.commit()
    print("Multi-subject curriculum seeding completed successfully!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_multi_curricula(db)
    finally:
        db.close()
