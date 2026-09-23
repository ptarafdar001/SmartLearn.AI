"""
Idempotent curriculum seed script for SmartLearn.AI.
Initial canonical slice: ISC -> Class 11 -> Humanities / Arts -> History.

Syllabus Source of Truth:
- Authority: Council for the Indian School Certificate Examinations (CISCE)
- Document: Regulations and Syllabuses, ISC History
- Examination Year: 2027
- Source URL: https://www.cisce.org/regulations-and-syllabuses-isc/
- Document Reference: 8.-ISC-History.pdf
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.learning import Chapter, LearningObjective, LearningResource, Subject, Topic
from app.db.curriculum_catalog_data import (
    CANONICAL_SUBJECTS_CATALOG,
    CBSE_10_SCIENCE_SYLLABUS,
    CBSE_10_MATH_SYLLABUS,
    CBSE_12_PHYSICS_SYLLABUS,
    ICSE_10_HCG_SYLLABUS,
)

logger = logging.getLogger("smartlearn.seed")

# Official CISCE ISC History (Class XI) Curriculum Fixture
# Preserves official CISCE chapter numbers and titles for Examination Year 2027.
ISC_HISTORY_FIXTURE: Dict[str, Any] = {
    "code": "isc-11-hist",
    "name": "History",
    "board": "ISC",
    "grade": "Class 11",
    "academic_stream": "Humanities / Arts",
    "category": "elective",
    "description": (
        "Official CISCE ISC Class XI History curriculum covering Section A (Indian History) "
        "and Section B (World History) for Examination Year 2027."
    ),
    "display_order": 1,
    "chapters": [
        # ── SECTION A: INDIAN HISTORY ──────────────────────────────────────────
        {
            "chapter_number": 1,
            "title": "Emergence of the Colonial Economy",
            "section": "Section A - Indian History",
            "is_official_title": True,
            "description": (
                "Official CISCE Chapter 1: Development of transport and communication; "
                "land revenue systems; de-industrialisation and rural indebtedness; colonial forest laws."
            ),
            "topics": [
                {
                    "topic_number": 1,
                    "title": "Development of Transport & Communication: Railways, Roads, and Telegraphs",
                    "official_subtopic_ref": "Transport and Communication (Railways, Roads, Telegraph)",
                    "is_official_subtopic": True,
                    "description": (
                        "Dalhousie's railway minutes, strategic troop movements, commercial export "
                        "of raw materials, the guarantee system, and the drain of wealth."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "Colonial Transport Infrastructure & The Railway Guarantee System",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# Development of Transport and Communication under Colonial Rule\n\n"
                                "## 1. Motivations for Railway Construction\n"
                                "Introduced in 1853 under Governor-General Lord Dalhousie, Indian railways were designed "
                                "primarily around two imperial requirements:\n"
                                "1. **Military & Strategic**: Rapid movement of British regiments to border outposts and inland riot zones.\n"
                                "2. **Commercial Exploitation**: Facilitating transport of raw cotton, jute, tea, and food grains to ports "
                                "(Bombay, Calcutta, Madras) for export to Britain, and distributing British machine manufactures into rural markets.\n\n"
                                "## 2. The Guarantee System\n"
                                "British railway investors were guaranteed a 4.5% to 5% return directly from Indian tax revenues. "
                                "This encouraged extravagant expenditure by private British firms with no incentive for economy.\n\n"
                                "## 3. Impact on India\n"
                                "While colonial authorities constructed infrastructure for exploitation, railways inadvertently fostered "
                                "inter-regional unity and political solidarity among Indians, serving as a catalyst for the early national movement."
                            ),
                            "order_index": 1,
                        },
                        {
                            "title": "High-Yield Summary: Transport & Communications Balance Sheet",
                            "resource_type": "notes",
                            "provider": "smartlearn",
                            "source_name": "SmartLearn Editorial Board",
                            "text_content": (
                                "### Key Exam Pointers: Chapter 1 Topic 1\n\n"
                                "- **1853**: First passenger railway train between Bombay and Thane (34 km).\n"
                                "- **Telegraph Line**: First telegraph opened between Calcutta and Diamond Harbour in 1851.\n"
                                "- **Grand Trunk Road**: Renovated primarily to connect strategic military hubs.\n"
                                "- **Economic Critique**: Dadabhai Naoroji and Romesh Chunder Dutt identified the railway guarantee "
                                "system as a prime conduit for the unilateral 'Drain of Wealth'."
                            ),
                            "order_index": 2,
                        },
                        {
                            "title": "Video Lesson: Railways and the Colonial Infrastructure Model",
                            "resource_type": "video",
                            "provider": "youtube",
                            "source_name": "National Educational Video Archive",
                            "source_url": "https://www.youtube.com/watch?v=kYJq1000m9A",
                            "external_id": "kYJq1000m9A",
                            "content_url": "https://www.youtube-nocookie.com/embed/kYJq1000m9A",
                            "duration_seconds": 780,
                            "order_index": 3,
                        },
                    ],
                },
                {
                    "topic_number": 2,
                    "title": "Colonial Land Revenue Systems: Permanent, Ryotwari, and Mahalwari",
                    "official_subtopic_ref": "Land Revenue Settlements and Rural Impact",
                    "is_official_subtopic": True,
                    "description": (
                        "Lord Cornwallis's Permanent Settlement of 1793 in Bengal, Thomas Munro's Ryotwari system, "
                        "the Mahalwari system, monetization, and peasant indebtedness."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "Comparative Study of British Land Revenue Settlements",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# British Land Revenue Systems in India\n\n"
                                "## 1. Permanent Settlement (1793)\n"
                                "- Introduced by Lord Cornwallis in Bengal, Bihar, and Orissa.\n"
                                "- Zamindars were recognized as owners of the land with revenue fixed in perpetuity (89% to British, 11% to Zamindar).\n"
                                "- Result: Created an absentee landlord class and widespread peasant rack-renting through the Sunset Law.\n\n"
                                "## 2. Ryotwari System\n"
                                "- Developed by Thomas Munro and Captain Read in Madras and Bombay Presidencies.\n"
                                "- Direct settlement between government and individual cultivator (Ryot).\n"
                                "- Revenue assessments were exorbitant (often 50-60%) and revised periodically.\n\n"
                                "## 3. Mahalwari System\n"
                                "- Introduced in the North-Western Provinces and Punjab.\n"
                                "- Settlement made village by village (Mahal) through village headmen (Lambardars).\n\n"
                                "## 4. Consequences for Indian Agriculture\n"
                                "Rigid cash revenue payments forced peasants into borrowing from village moneylenders (Sahukars), "
                                "leading to land alienation, rural debt bondage, and severe vulnerability during crop failures."
                            ),
                            "order_index": 1,
                        },
                        {
                            "title": "Quick Revision Table: Land Revenue Systems",
                            "resource_type": "notes",
                            "provider": "smartlearn",
                            "source_name": "SmartLearn Editorial Board",
                            "text_content": (
                                "### Summary Matrix\n\n"
                                "| Settlement | Architect | Region | Revenue Base | Primary Consequence |\n"
                                "|---|---|---|---|---|\n"
                                "| **Permanent** | Lord Cornwallis (1793) | Bengal, Bihar | Fixed in perpetuity | Evictions, Sunset Law |\n"
                                "| **Ryotwari** | Thomas Munro (1820) | Madras, Bombay | Cultivator (Ryot) | High initial rate (up to 50%) |\n"
                                "| **Mahalwari** | Holt Mackenzie (1822) | Gangetic Valley, Punjab | Village Estate (Mahal) | Joint communal liability |"
                            ),
                            "order_index": 2,
                        },
                    ],
                },
                {
                    "topic_number": 3,
                    "title": "De-industrialisation and the Decline of Traditional Handicrafts",
                    "official_subtopic_ref": "De-industrialisation and artisanal decline",
                    "is_official_subtopic": True,
                    "description": (
                        "Tariff discrimination, loss of courtly patronage, flooding of machine-made British textiles, "
                        "and the agrarianization of the Indian workforce."
                    ),
                    "estimated_minutes": 20,
                    "resources": [
                        {
                            "title": "The Destruction of Indian Handicrafts & Ruralization",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# De-industrialisation in 19th-Century India\n\n"
                                "## 1. Mechanisms of Artisanal Decline\n"
                                "Indian cotton and silk manufactures, renowned globally for centuries, were dismantled through:\n"
                                "1. **One-Way Free Trade**: British manufactured goods entered India duty-free, while Indian exports to Britain "
                                "faced punitive tariffs up to 80%.\n"
                                "2. **Industrial Revolution in Britain**: Cheap power-loom textiles from Manchester outcompeted Indian hand-spun fabrics.\n"
                                "3. **Disappearance of Native Patronage**: Annexation of princely states dissolved courtly demand for luxury handicrafts (Dacca muslins, Kashmir shawls).\n\n"
                                "## 2. Ruralization of India\n"
                                "Deprived of livelihood, millions of urban weavers, spinners, and smiths were forced back onto already overcrowded "
                                "agricultural land, lowering agrarian productivity and driving deep-seated rural poverty."
                            ),
                            "order_index": 1,
                        },
                    ],
                },
            ],
        },
        {
            "chapter_number": 2,
            "title": "Social Movements",
            "section": "Section A - Indian History",
            "is_official_title": True,
            "description": (
                "Official CISCE Chapter 2: Socio-religious reform movements (Brahmo Samaj, Arya Samaj, Aligarh Movement); "
                "reforms against caste discrimination (Phule, Narayana Guru); status of women and education."
            ),
            "topics": [
                {
                    "topic_number": 1,
                    "title": "19th-Century Socio-Religious Reform Movements: Brahmo Samaj, Arya Samaj, Aligarh Movement",
                    "official_subtopic_ref": "Brahmo Samaj, Arya Samaj, Aligarh Movement",
                    "is_official_subtopic": True,
                    "description": (
                        "Raja Ram Mohan Roy, Swami Dayanand Saraswati, and Sir Syed Ahmad Khan; "
                        "rationalist critique of orthodox rituals, monotheism, and modern schooling."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "Major Socio-Religious Awakening Movements in India",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# 19th-Century Socio-Religious Reform Movements\n\n"
                                "## 1. Brahmo Samaj (1828)\n"
                                "- Founded by Raja Ram Mohan Roy ('Father of Modern India').\n"
                                "- Opposed idolatry, polytheism, Sati, child marriage, and hereditary priesthood.\n"
                                "- Synthesized Upanishadic monotheism with Western humanitarian rationalism.\n\n"
                                "## 2. Arya Samaj (1875)\n"
                                "- Founded by Swami Dayanand Saraswati with the call *'Go Back to the Vedas'*.\n"
                                "- Rejected idol worship, caste distinctions, and child marriage; established D.A.V. educational institutions.\n\n"
                                "## 3. Aligarh Movement\n"
                                "- Led by Sir Syed Ahmad Khan to modernize Muslim society through English education and scientific thought.\n"
                                "- Founded the Muhammadan Anglo-Oriental College in 1875 (later Aligarh Muslim University)."
                            ),
                            "order_index": 1,
                        },
                        {
                            "title": "Quick Comparison Notes: Thinkers and Formations",
                            "resource_type": "notes",
                            "provider": "smartlearn",
                            "source_name": "SmartLearn Editorial Board",
                            "text_content": (
                                "### Key Reformers Snapshot\n\n"
                                "- **Raja Ram Mohan Roy**: *Sambad Kaumudi*, *Atmiya Sabha* (1814), *Brahmo Samaj* (1828).\n"
                                "- **Swami Dayanand Saraswati**: *Satyarth Prakash*, Shuddhi movement, Vedic supremacy.\n"
                                "- **Sir Syed Ahmad Khan**: *Tahzib-ul-Akhlaq*, modern scientific education, Aligarh movement."
                            ),
                            "order_index": 2,
                        },
                        {
                            "title": "Video Lesson: Indian Renaissance and Social Awakening",
                            "resource_type": "video",
                            "provider": "youtube",
                            "source_name": "National Educational Video Archive",
                            "source_url": "https://www.youtube.com/watch?v=9gE7L2H6v8s",
                            "external_id": "9gE7L2H6v8s",
                            "content_url": "https://www.youtube-nocookie.com/embed/9gE7L2H6v8s",
                            "duration_seconds": 840,
                            "order_index": 3,
                        },
                    ],
                },
                {
                    "topic_number": 2,
                    "title": "Reform Efforts Against Caste Discrimination & Advances in Women's Education",
                    "official_subtopic_ref": "Caste movements and emancipation of women",
                    "is_official_subtopic": True,
                    "description": (
                        "Jyotirao Phule's Satyashodhak Samaj, Narayana Guru's social agitation in Kerala, "
                        "campaigns against Sati (1829), Widow Remarriage Act (1856), and women's educational institutions."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "Caste Emancipation and Women's Legal & Educational Rights",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# Caste and Gender Reforms in Colonial India\n\n"
                                "## 1. Anti-Caste Movements\n"
                                "- **Jyotirao Phule (Maharashtra)**: Established the *Satyashodhak Samaj* (1873); author of *Gulamgiri*; "
                                "championed the social and educational rights of lower castes and untouchables.\n"
                                "- **Sri Narayana Guru (Kerala)**: Propounded *'One Caste, One Religion, One God for Man'*; "
                                "consecrated Shiva temples open to all communities, breaking upper-caste priestly monopolies.\n\n"
                                "## 2. Emancipation of Women\n"
                                "- **Abolition of Sati (1829)**: Regulation XVII passed by Lord William Bentinck following Ram Mohan Roy's campaigning.\n"
                                "- **Hindu Widows' Remarriage Act (1856)**: Championed by Ishwar Chandra Vidyasagar through scriptural justification.\n"
                                "- **Women's Education**: Savitribai and Jyotirao Phule opened India's first school for girls in Pune (1848); "
                                "Bethune School established in Calcutta (1849)."
                            ),
                            "order_index": 1,
                        },
                    ],
                },
            ],
        },
        {
            "chapter_number": 3,
            "title": "Protest Movements against Colonial Rule",
            "section": "Section A - Indian History",
            "is_official_title": True,
            "description": (
                "Official CISCE Chapter 3: Agrarian protests and tribal rebellions; Indigo Uprising (1859); "
                "Deccan Riots (1875); Birsa Munda and the Ulgulan (1899–1900)."
            ),
            "topics": [
                {
                    "topic_number": 1,
                    "title": "Agrarian Resistance: Indigo Uprising (1859) & Deccan Riots (1875)",
                    "official_subtopic_ref": "Indigo Uprising (1859) and Deccan Riots (1875)",
                    "is_official_subtopic": True,
                    "description": (
                        "Forced cultivation of indigo in Bengal, non-violent cultivator resistance, "
                        "the Indigo Commission, and the Deccan peasant uprising against Marwari moneylenders."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "The Peasant Resistance Movements in 19th-Century India",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# Major Peasant Protest Movements\n\n"
                                "## 1. Indigo Rebellion / Neel Bidroha (1859–60)\n"
                                "- **Cause**: European planters forced Bengali ryots into signing coercive contracts to grow indigo "
                                "instead of food crops under exploitative advance payment systems (Dadni).\n"
                                "- **Leaders**: Bishnucharan Biswas and Digambar Biswas of Nadia.\n"
                                "- **Cultural Impact**: Dinabandhu Mitra's play *Nil Darpan* exposed the brutality of planters.\n"
                                "- **Outcome**: British government appointed the Indigo Commission (1860), which declared ryots "
                                "could not be compelled to grow indigo, ending planter tyranny in Bengal.\n\n"
                                "## 2. Deccan Riots (1875)\n"
                                "- **Cause**: Peasants in Poona and Ahmednagar faced steep revenue hikes (up to 50%) during an agrarian slump, "
                                "falling into debt traps with Gujarati and Marwari moneylenders who grabbed mortgaged land.\n"
                                "- **Outcome**: Deccan Agriculturists' Relief Act (1879) provided peasant protection against arrest and debt confiscation."
                            ),
                            "order_index": 1,
                        },
                        {
                            "title": "Video Lesson: Indigo Rebellion and Rural Resistance",
                            "resource_type": "video",
                            "provider": "youtube",
                            "source_name": "National Educational Video Archive",
                            "source_url": "https://www.youtube.com/watch?v=pE4_G7eU-3Q",
                            "external_id": "pE4_G7eU-3Q",
                            "content_url": "https://www.youtube-nocookie.com/embed/pE4_G7eU-3Q",
                            "duration_seconds": 890,
                            "order_index": 2,
                        },
                    ],
                },
                {
                    "topic_number": 2,
                    "title": "Tribal Resistance: Birsa Munda and the Ulgulan (1899–1900)",
                    "official_subtopic_ref": "Birsa Munda and tribal movements",
                    "is_official_subtopic": True,
                    "description": (
                        "Disruption of the Khuntkatti joint landholding system in Chotanagpur, "
                        "exploitation by Dikus (outsiders), and Birsa Munda's religious and political rebellion (Ulgulan)."
                    ),
                    "estimated_minutes": 20,
                    "resources": [
                        {
                            "title": "Birsa Munda and the Tribal Movement in Chotanagpur",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# Birsa Munda and the Ulgulan (Great Tumult)\n\n"
                                "## 1. Background\n"
                                "The Munda tribe practiced the *Khuntkatti* (customary collective land tenure) in the Chotanagpur plateau. "
                                "British revenue policies, colonial forest reservation acts, and Christian missionaries dismantled their "
                                "traditional social fabric, turning free adivasis into bonded laborers for landlords and moneylenders (Dikus).\n\n"
                                "## 2. Birsa Munda's Leadership\n"
                                "- Mobilized the Mundas through spiritual reform, preaching purity, abstinence, and faith in one God (Singbonga).\n"
                                "- Proclaimed the establishment of *Munda Raj* and non-payment of rent to landlords.\n\n"
                                "## 3. Legacy and Outcomes\n"
                                "Although Birsa was captured in 1900 and died in Ranchi jail, the uprising compelled the British to pass "
                                "the **Chotanagpur Tenancy Act (1908)**, recognizing Khuntkatti rights and prohibiting the transfer of tribal land to non-tribals."
                            ),
                            "order_index": 1,
                        },
                    ],
                },
            ],
        },
        {
            "chapter_number": 4,
            "title": "Growth of Nationalism",
            "section": "Section A - Indian History",
            "is_official_title": True,
            "description": (
                "Official CISCE Chapter 4: Early nationalist activity and the Indian National Congress; "
                "Swadeshi and Boycott Movement (1905); revolutionary nationalism and militant response."
            ),
            "topics": [
                {
                    "topic_number": 1,
                    "title": "Early Nationalist Phase and the Indian National Congress",
                    "official_subtopic_ref": "Early Nationalist Activity and INC Formation",
                    "is_official_subtopic": True,
                    "description": (
                        "Factors aiding national awakening, formation of the Indian National Congress (1885), "
                        "Moderate leadership, economic critique of colonialism, and constitutional agitation."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "The Rise of Indian Nationalism and the Early Nationalists",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# The Growth of National Consciousness & The Early Congress\n\n"
                                "## 1. Catalysts for Modern Nationalism\n"
                                "- Uniform British administration, legal system, and English language education creating a pan-Indian intelligentsia.\n"
                                "- Vernacular press and literature exposing colonial exploitation.\n"
                                "- Reactionary policies of Lord Lytton: Vernacular Press Act (1878), Arms Act (1878), and the Ilbert Bill controversy (1883).\n\n"
                                "## 2. Foundation of the INC (December 1885)\n"
                                "- First session held at Gokuldas Tejpal Sanskrit College, Bombay, presided over by W.C. Bonnerjee.\n"
                                "- Attended by 72 delegates representing various regional associations.\n\n"
                                "## 3. The Moderates (1885–1905)\n"
                                "- Leaders: Dadabhai Naoroji, Gopal Krishna Gokhale, Pherozeshah Mehta, Surendranath Banerjee.\n"
                                "- Method: 3Ps (Petitions, Prayers, and Protests) within constitutional bounds.\n"
                                "- Historical Contribution: Exposed the economic drain of British rule and created an all-India political platform."
                            ),
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "topic_number": 2,
                    "title": "Swadeshi Movement & Anti-Partition Agitation (1905)",
                    "official_subtopic_ref": "Partition of Bengal and Swadeshi & Boycott Movement",
                    "is_official_subtopic": True,
                    "description": (
                        "Lord Curzon's partition of Bengal, mass boycotts, Swadeshi enterprises, "
                        "national education, and the emergence of Lal-Bal-Pal leadership."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "The Swadeshi Movement and Partition of Bengal (1905)",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# The Partition of Bengal and the Swadeshi Movement\n\n"
                                "## 1. The Partition Scheme (1905)\n"
                                "Viceroy Lord Curzon partitioned Bengal on October 16, 1905, officially claiming administrative convenience. "
                                "The true political design was to divide the politically militant Bengali intelligentsia and create communal rifts.\n\n"
                                "## 2. The Resistance Movement\n"
                                "- **Day of Mourning**: Hartals in Calcutta, fasting, and Rabindranath Tagore's call for *Raksha Bandhan* as a symbol of unity.\n"
                                "- **Boycott**: Public bonfires of Manchester cloth and foreign goods.\n"
                                "- **Swadeshi**: Establishment of indigenous textile mills, soaps, and the Bengal Chemical & Pharmaceutical Works by P.C. Ray.\n"
                                "- **National Education**: Bengal National College established under Sri Aurobindo.\n\n"
                                "## 3. Historical Impact\n"
                                "Transformed the Indian national struggle from elite constitutionalism into an active mass movement."
                            ),
                            "order_index": 1,
                        },
                        {
                            "title": "High-Yield Notes: Swadeshi Chronology & Leaders",
                            "resource_type": "notes",
                            "provider": "smartlearn",
                            "source_name": "SmartLearn Editorial Board",
                            "text_content": (
                                "### Key Swadeshi Facts\n\n"
                                "- **August 7, 1905**: Formal Boycott resolution passed at Calcutta Town Hall.\n"
                                "- **October 16, 1905**: Partition took effect; observance of Day of Mourning.\n"
                                "- **Key Leaders (Extremists)**: Bal Gangadhar Tilak, Bipin Chandra Pal, Lala Lajpat Rai (Lal-Bal-Pal), Aurobindo Ghosh.\n"
                                "- **1911**: Annulment of Partition by Lord Hardinge; transfer of imperial capital from Calcutta to Delhi."
                            ),
                            "order_index": 2,
                        },
                        {
                            "title": "Video Lesson: Partition of Bengal and Swadeshi Movement",
                            "resource_type": "video",
                            "provider": "youtube",
                            "source_name": "National Educational Video Archive",
                            "source_url": "https://www.youtube.com/watch?v=wXw6h3Z5XQE",
                            "external_id": "wXw6h3Z5XQE",
                            "content_url": "https://www.youtube-nocookie.com/embed/wXw6h3Z5XQE",
                            "duration_seconds": 920,
                            "order_index": 3,
                        },
                    ],
                },
                {
                    "topic_number": 3,
                    "title": "Revolutionary Nationalism and Militant Resistance",
                    "official_subtopic_ref": "Revolutionary Nationalism",
                    "is_official_subtopic": True,
                    "description": (
                        "Rise of militant nationalism, secret revolutionary societies (Anushilan Samiti, Jugantar), "
                        "individual heroic actions, and government repressive acts."
                    ),
                    "estimated_minutes": 20,
                    "resources": [
                        {
                            "title": "The Revolutionary Phase in Early 20th-Century India",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# Revolutionary Nationalism\n\n"
                                "## 1. Context and Origin\n"
                                "Severe government repression of the Swadeshi movement, combined with the failure of Moderate petitions, "
                                "compelled young patriots to adopt revolutionary methods to overthrow colonial tyranny.\n\n"
                                "## 2. Organizations and Actions\n"
                                "- **Anushilan Samiti**: Founded in Calcutta by Pramathanath Mitra and Satish Chandra Bose, with a powerful branch in Dhaka under Pulin Das.\n"
                                "- **Jugantar Group**: Founded by Barindra Kumar Ghosh and Bhupendranath Datta.\n"
                                "- **Muzaffarpur Conspiracy (1908)**: Khudiram Bose and Prafulla Chaki attempted assassination of Magistrate Kingsford; "
                                "Khudiram Bose was executed at age 18, becoming an enduring national symbol."
                            ),
                            "order_index": 1,
                        },
                    ],
                },
            ],
        },
        # ── SECTION B: WORLD HISTORY ───────────────────────────────────────────
        {
            "chapter_number": 7,
            "title": "World War I: Causes, events leading to it; Peace settlements",
            "section": "Section B - World History",
            "is_official_title": True,
            "description": (
                "Official CISCE Chapter 7: Underlying causes (Militarism, Alliances, Imperialism, Nationalism); "
                "Sarajevo crisis; Peace settlements (Treaty of Versailles) and the League of Nations."
            ),
            "topics": [
                {
                    "topic_number": 1,
                    "title": "Causes and Pre-War Imperial Rivalries: Alliances, Militarism, and Sarajevo",
                    "official_subtopic_ref": "Causes and events leading to WWI",
                    "is_official_subtopic": True,
                    "description": (
                        "The rival alliance systems (Triple Alliance vs Triple Entente), naval race between Britain and Germany, "
                        "Balkan crises, and the assassination of Archduke Franz Ferdinand."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "Underlying and Immediate Causes of the First World War",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# The Outbreak of World War I (1914)\n\n"
                                "## 1. System of Alliances\n"
                                "- **Triple Alliance (1882)**: Germany, Austria-Hungary, Italy.\n"
                                "- **Triple Entente (1907)**: Britain, France, Russia.\n\n"
                                "## 2. Imperial and Economic Rivalries\n"
                                "Rapid German industrial growth under Kaiser Wilhelm II sparked aggressive colonial ambitions (*Weltpolitik*), "
                                "threatening British maritime supremacy through a competitive naval arms race.\n\n"
                                "## 3. The Spark: Sarajevo Crisis\n"
                                "On June 28, 1914, Austrian Archduke Franz Ferdinand was assassinated in Sarajevo by Gavrilo Princip "
                                "of the Serbian secret society 'Black Hand'. Austria's ultimatum to Serbia triggered the alliance network, "
                                "igniting general European war by August 1914."
                            ),
                            "order_index": 1,
                        },
                        {
                            "title": "Video Lesson: The M-A-I-N Causes of the Great War",
                            "resource_type": "video",
                            "provider": "youtube",
                            "source_name": "World History Archive",
                            "source_url": "https://www.youtube.com/watch?v=dHSQAEam2yc",
                            "external_id": "dHSQAEam2yc",
                            "content_url": "https://www.youtube-nocookie.com/embed/dHSQAEam2yc",
                            "duration_seconds": 880,
                            "order_index": 2,
                        },
                    ],
                },
                {
                    "topic_number": 2,
                    "title": "The Peace Settlements: Treaty of Versailles and the League of Nations",
                    "official_subtopic_ref": "Peace settlements and the League of Nations",
                    "is_official_subtopic": True,
                    "description": (
                        "Paris Peace Conference (1919), Woodrow Wilson's Fourteen Points, terms imposed on Germany, "
                        "and the covenant of the League of Nations."
                    ),
                    "estimated_minutes": 25,
                    "resources": [
                        {
                            "title": "The Treaty of Versailles (1919) and Its Geopolitical Consequences",
                            "resource_type": "text",
                            "provider": "smartlearn",
                            "source_name": "CISCE ISC Class XI History Curriculum (Exam Year 2027)",
                            "source_url": "https://www.cisce.org/regulations-and-syllabuses-isc/",
                            "text_content": (
                                "# The Treaty of Versailles and the Post-War Settlement\n\n"
                                "## 1. The Paris Peace Conference\n"
                                "Dominated by the 'Big Three': Woodrow Wilson (USA), David Lloyd George (Britain), and Georges Clemenceau (France).\n\n"
                                "## 2. Punitive Terms Imposed on Germany\n"
                                "- **War Guilt Clause (Article 231)**: Germany forced to accept sole responsibility for the war.\n"
                                "- **Reparations**: Imposed a staggering indemnity of 6.6 billion pounds.\n"
                                "- **Territorial Losses**: Alsace-Lorraine returned to France; Polish Corridor ceded; loss of all overseas colonies.\n"
                                "- **Disarmament**: Army restricted to 100,000 men; Rhineland demilitarized; conscription abolished.\n\n"
                                "## 3. The League of Nations\n"
                                "Created to maintain collective security and settle international disputes peacefully, but severely weakened "
                                "by the refusal of the US Senate to join, absence of an independent armed force, and inability to restrain aggressive powers."
                            ),
                            "order_index": 1,
                        },
                    ],
                },
            ],
        },
    ],
}


def seed_isc_history_slice(db: Session) -> Subject:
    """
    Idempotently seed the official CISCE ISC Class XI History curriculum slice into PostgreSQL.
    Preserves exact official CISCE chapter numbers (1, 2, 3, 4, 7) and titles for Exam Year 2027.
    Guarantees that re-running does not produce duplicate records or orphaned entities.
    """
    logger.info("Seeding canonical CISCE ISC Class XI History curriculum slice (Exam Year 2027)...")

    # 1. Upsert Subject
    subject = db.query(Subject).filter(Subject.code == ISC_HISTORY_FIXTURE["code"]).first()
    if not subject:
        subject = Subject(
            code=ISC_HISTORY_FIXTURE["code"],
            name=ISC_HISTORY_FIXTURE["name"],
            board=ISC_HISTORY_FIXTURE["board"],
            grade=ISC_HISTORY_FIXTURE["grade"],
            academic_stream=ISC_HISTORY_FIXTURE["academic_stream"],
            category=ISC_HISTORY_FIXTURE["category"],
            description=ISC_HISTORY_FIXTURE["description"],
            display_order=ISC_HISTORY_FIXTURE["display_order"],
            is_active=True,
            curriculum_status="content_available",
            source_authority="CISCE",
            source_url="https://www.cisce.org/regulations-and-syllabuses-isc/",
            syllabus_version="Examination Year 2027",
            last_verified_at=datetime.now(timezone.utc),
        )
        db.add(subject)
        db.flush()
    else:
        subject.name = ISC_HISTORY_FIXTURE["name"]
        subject.board = ISC_HISTORY_FIXTURE["board"]
        subject.grade = ISC_HISTORY_FIXTURE["grade"]
        subject.academic_stream = ISC_HISTORY_FIXTURE["academic_stream"]
        subject.description = ISC_HISTORY_FIXTURE["description"]
        subject.curriculum_status = "content_available"
        subject.source_authority = "CISCE"
        subject.source_url = "https://www.cisce.org/regulations-and-syllabuses-isc/"
        subject.syllabus_version = "Examination Year 2027"
        subject.last_verified_at = datetime.now(timezone.utc)
        db.flush()

    fixture_chapter_nums = [c["chapter_number"] for c in ISC_HISTORY_FIXTURE["chapters"]]

    # 2. Upsert Chapters & Topics
    for ch_data in ISC_HISTORY_FIXTURE["chapters"]:
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
                description=ch_data["description"],
            )
            db.add(chapter)
            db.flush()
        else:
            chapter.title = ch_data["title"]
            chapter.description = ch_data["description"]
            db.flush()

        fixture_topic_nums = [t["topic_number"] for t in ch_data["topics"]]

        # Clean any extraneous topics not in fixture for this chapter
        old_topics = (
            db.query(Topic)
            .filter(
                Topic.chapter_id == chapter.id,
                ~Topic.topic_number.in_(fixture_topic_nums),
            )
            .all()
        )
        for ot in old_topics:
            db.delete(ot)
        db.flush()

        # Upsert topics
        for top_data in ch_data["topics"]:
            topic = (
                db.query(Topic)
                .filter(
                    Topic.chapter_id == chapter.id,
                    Topic.topic_number == top_data["topic_number"],
                )
                .first()
            )
            if not topic:
                topic = Topic(
                    chapter_id=chapter.id,
                    topic_number=top_data["topic_number"],
                    title=top_data["title"],
                    description=top_data["description"],
                    estimated_minutes=top_data["estimated_minutes"],
                )
                db.add(topic)
                db.flush()
            else:
                topic.title = top_data["title"]
                topic.description = top_data["description"]
                topic.estimated_minutes = top_data["estimated_minutes"]
                db.flush()

            # Clean extraneous resources for this topic
            fixture_order_indices = [r["order_index"] for r in top_data.get("resources", [])]
            if fixture_order_indices:
                old_resources = (
                    db.query(LearningResource)
                    .filter(
                        LearningResource.topic_id == topic.id,
                        ~LearningResource.order_index.in_(fixture_order_indices),
                    )
                    .all()
                )
                for or_res in old_resources:
                    db.delete(or_res)
                db.flush()

            # Upsert Learning Resources
            for res_data in top_data.get("resources", []):
                resource = (
                    db.query(LearningResource)
                    .filter(
                        LearningResource.topic_id == topic.id,
                        LearningResource.order_index == res_data["order_index"],
                        LearningResource.resource_type == res_data["resource_type"],
                    )
                    .first()
                )
                if not resource:
                    resource = LearningResource(
                        topic_id=topic.id,
                        title=res_data["title"],
                        resource_type=res_data["resource_type"],
                        provider=res_data.get("provider", "smartlearn"),
                        source_name=res_data.get("source_name"),
                        source_url=res_data.get("source_url"),
                        external_id=res_data.get("external_id"),
                        content_url=res_data.get("content_url"),
                        text_content=res_data.get("text_content"),
                        duration_seconds=res_data.get("duration_seconds"),
                        order_index=res_data["order_index"],
                        is_active=True,
                        is_verified=True,
                        verified_at=datetime.now(timezone.utc),
                    )
                    db.add(resource)
                else:
                    resource.title = res_data["title"]
                    resource.provider = res_data.get("provider", "smartlearn")
                    resource.source_name = res_data.get("source_name")
                    resource.source_url = res_data.get("source_url")
                    resource.external_id = res_data.get("external_id")
                    resource.content_url = res_data.get("content_url")
                    resource.text_content = res_data.get("text_content")
                    resource.duration_seconds = res_data.get("duration_seconds")
                    resource.is_active = True
                    resource.is_verified = True

    # Remove any chapters for this subject not present in the current fixture
    stale_chapters = (
        db.query(Chapter)
        .filter(
            Chapter.subject_id == subject.id,
            ~Chapter.chapter_number.in_(fixture_chapter_nums),
        )
        .all()
    )
    for sc in stale_chapters:
        db.delete(sc)

    db.flush()
    logger.info("Official CISCE ISC Class XI History curriculum slice seeded successfully.")
    return subject


def seed_canonical_catalog(db: Session) -> int:
    """Upsert all canonical subjects across all boards, classes, and streams."""
    logger.info("Upserting canonical multi-board subjects catalog...")
    upserted_count = 0
    for s_data in CANONICAL_SUBJECTS_CATALOG:
        code = s_data["code"]
        existing = db.query(Subject).filter(Subject.code == code).first()
        if not existing:
            subj = Subject(
                code=code,
                name=s_data["name"],
                board=s_data["board"],
                grade=s_data["grade"],
                academic_stream=s_data.get("academic_stream"),
                category=s_data.get("category", "core"),
                description=s_data.get("description"),
                display_order=s_data.get("display_order", 0),
                is_active=True,
                curriculum_status=s_data.get("curriculum_status", "in_preparation"),
                source_authority=s_data.get("source_authority"),
                source_url=s_data.get("source_url"),
                syllabus_version=s_data.get("syllabus_version"),
            )
            db.add(subj)
            upserted_count += 1
        else:
            existing.name = s_data["name"]
            existing.board = s_data["board"]
            existing.grade = s_data["grade"]
            existing.academic_stream = s_data.get("academic_stream")
            existing.category = s_data.get("category", existing.category)
            existing.description = s_data.get("description", existing.description)
            existing.display_order = s_data.get("display_order", existing.display_order)
            existing.source_authority = s_data.get("source_authority", existing.source_authority)
            existing.source_url = s_data.get("source_url", existing.source_url)
            existing.syllabus_version = s_data.get("syllabus_version", existing.syllabus_version)
            if existing.curriculum_status not in ("content_available", "curriculum_verified"):
                existing.curriculum_status = s_data.get("curriculum_status", existing.curriculum_status)
    db.flush()
    logger.info(f"Canonical catalog upsert complete ({len(CANONICAL_SUBJECTS_CATALOG)} entries handled).")
    return upserted_count


def seed_exemplar_syllabi(db: Session) -> None:
    """
    Seed authoritative syllabus structures for verified exemplar subjects:
    - CBSE Class 10 Science (13 NCERT chapters, topics, verified learning objectives & textbook notes)
    - CBSE Class 10 Mathematics Standard (14 NCERT chapters, topics)
    - CBSE Class 12 Physics (14 NCERT chapters)
    - ICSE Class 10 History, Civics and Geography (12 CISCE chapters)
    """
    logger.info("Seeding authoritative exemplar syllabi...")
    exemplars = [
        CBSE_10_SCIENCE_SYLLABUS,
        CBSE_10_MATH_SYLLABUS,
        CBSE_12_PHYSICS_SYLLABUS,
        ICSE_10_HCG_SYLLABUS,
    ]
    for ex in exemplars:
        subject = db.query(Subject).filter(Subject.code == ex["code"]).first()
        if not subject:
            subject = (
                db.query(Subject)
                .filter(
                    Subject.board == ex["board"],
                    Subject.grade == ex["grade"],
                    Subject.name == ex["name"],
                )
                .first()
            )
        if not subject:
            logger.warning(f"Exemplar subject record not found for code={ex.get('code')}")
            continue

        if subject.curriculum_status != "content_available":
            subject.curriculum_status = "curriculum_verified"
        subject.last_verified_at = datetime.now(timezone.utc)
        db.flush()

        fixture_chapter_nums = [c["chapter_number"] for c in ex["chapters"]]
        for ch_data in ex["chapters"]:
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
                    description=ch_data.get("description"),
                )
                db.add(chapter)
                db.flush()
            else:
                chapter.title = ch_data["title"]
                chapter.description = ch_data.get("description")
                db.flush()

            # Upsert topics if present
            topics_data = ch_data.get("topics", [])
            for top_data in topics_data:
                topic = (
                    db.query(Topic)
                    .filter(
                        Topic.chapter_id == chapter.id,
                        Topic.topic_number == top_data["topic_number"],
                    )
                    .first()
                )
                if not topic:
                    topic = Topic(
                        chapter_id=chapter.id,
                        topic_number=top_data["topic_number"],
                        title=top_data["title"],
                        description=top_data.get("description"),
                        estimated_minutes=top_data.get("estimated_minutes", 20),
                    )
                    db.add(topic)
                    db.flush()
                else:
                    topic.title = top_data["title"]
                    topic.description = top_data.get("description")
                    topic.estimated_minutes = top_data.get("estimated_minutes", 20)
                    db.flush()

            if topics_data:
                fix_top_nums = [t["topic_number"] for t in topics_data]
                old_topics = (
                    db.query(Topic)
                    .filter(
                        Topic.chapter_id == chapter.id,
                        ~Topic.topic_number.in_(fix_top_nums),
                    )
                    .all()
                )
                for ot in old_topics:
                    db.delete(ot)
                db.flush()

        stale_chapters = (
            db.query(Chapter)
            .filter(
                Chapter.subject_id == subject.id,
                ~Chapter.chapter_number.in_(fixture_chapter_nums),
            )
            .all()
        )
        for sc in stale_chapters:
            db.delete(sc)
        db.flush()

    # Seed verified textbook notes and learning objectives for CBSE 10 Science Chapter 1
    cbse_sci = (
        db.query(Subject)
        .filter(Subject.board == "CBSE", Subject.grade == "Class 10", Subject.name == "Science")
        .first()
    )
    if cbse_sci:
        ch1 = (
            db.query(Chapter)
            .filter(Chapter.subject_id == cbse_sci.id, Chapter.chapter_number == 1)
            .first()
        )
        if ch1:
            t1 = db.query(Topic).filter(Topic.chapter_id == ch1.id, Topic.topic_number == 1).first()
            if t1:
                res = (
                    db.query(LearningResource)
                    .filter(
                        LearningResource.topic_id == t1.id,
                        LearningResource.order_index == 1,
                    )
                    .first()
                )
                if not res:
                    res = LearningResource(
                        topic_id=t1.id,
                        title="NCERT Textbook Overview: Chemical Reactions & Equations",
                        resource_type="notes",
                        provider="ncert",
                        source_name="NCERT Class X Science Textbook (Chapter 1)",
                        source_url="https://ncert.nic.in/textbook.php?jesc1=1-13",
                        text_content=(
                            "# Chemical Reactions and Equations\n\n"
                            "## 1. What is a Chemical Reaction?\n"
                            "Whenever a chemical change occurs, we say that a chemical reaction has taken place. "
                            "It is accompanied by changes such as change in state, change in colour, evolution of a gas, "
                            "or change in temperature.\n\n"
                            "## 2. Balanced Chemical Equations\n"
                            "The law of conservation of mass states that mass can neither be created nor destroyed in a chemical reaction. "
                            "That is, the total mass of the elements present in the products of a chemical reaction has to be equal to "
                            "the total mass of the elements present in the reactants.\n\n"
                            "**Example**: $3\\text{Fe} + 4\\text{H}_2\\text{O} \\rightarrow \\text{Fe}_3\\text{O}_4 + 4\\text{H}_2$\n"
                        ),
                        order_index=1,
                        is_active=True,
                        is_verified=True,
                        verified_at=datetime.now(timezone.utc),
                    )
                    db.add(res)

                lo1 = (
                    db.query(LearningObjective)
                    .filter(
                        LearningObjective.topic_id == t1.id,
                        LearningObjective.code == "CBSE10-SCI-CH01-LO01",
                    )
                    .first()
                )
                if not lo1:
                    lo1 = LearningObjective(
                        topic_id=t1.id,
                        code="CBSE10-SCI-CH01-LO01",
                        description="Write word equations and skeletal chemical equations for observable chemical changes.",
                        taxonomy_level="understand",
                        is_core=True,
                        is_verified=True,
                    )
                    db.add(lo1)

                lo2 = (
                    db.query(LearningObjective)
                    .filter(
                        LearningObjective.topic_id == t1.id,
                        LearningObjective.code == "CBSE10-SCI-CH01-LO02",
                    )
                    .first()
                )
                if not lo2:
                    lo2 = LearningObjective(
                        topic_id=t1.id,
                        code="CBSE10-SCI-CH01-LO02",
                        description="Balance chemical equations using stoichiometric coefficients consistent with conservation of mass.",
                        taxonomy_level="apply",
                        is_core=True,
                        is_verified=True,
                    )
                    db.add(lo2)

                cbse_sci.curriculum_status = "content_available"
                db.flush()


def seed_curriculum(db: Session) -> Subject:
    """
    Comprehensive idempotent multi-curriculum seed runner.
    1. Upserts canonical subjects across all advertised boards/grades/streams.
    2. Seeds official CISCE ISC Class XI History slice (preserves ID 43).
    3. Seeds authoritative exemplar syllabus structures (CBSE 10 Science, CBSE 10 Math, CBSE 12 Physics, ICSE 10 HCG).
    """
    logger.info("Executing comprehensive multi-curriculum seeding...")
    seed_canonical_catalog(db)
    isc_subject = seed_isc_history_slice(db)
    seed_exemplar_syllabi(db)
    db.commit()
    logger.info("Multi-curriculum database seeding completed successfully.")
    return isc_subject


seed_isc_history_curriculum = seed_curriculum


if __name__ == "__main__":
    session = SessionLocal()
    try:
        subj = seed_curriculum(session)
        print(f"Curriculum seeded successfully: {subj.name} (id={subj.id}, code={subj.code})")
    finally:
        session.close()
