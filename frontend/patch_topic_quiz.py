with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = "const getDynamicFallbackQuiz = (subject: string, topicName: string): QuizQuestion[] => ["
end_marker = "export const TopicStudyPage: React.FC = () => {"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_func = """const getDynamicFallbackQuiz = (subject: string, topicName: string): QuizQuestion[] => {
  const isLanguage = /hindi|sanskrit|bengali|marathi|tamil|telugu|urdu|gujarati|kannada|language/i.test(subject);
  if (isLanguage) {
    return [
      {
        id: 1,
        question: `${topicName} के अध्ययन का मुख्य उद्देश्य क्या है? (Primary objective of studying ${topicName})`,
        options: [
          'व्याकरणिक शुद्धता, अर्थ-ग्रहण और भाषा की अभिव्यक्ति क्षमता का विकास (Grammatical precision and comprehension)',
          'केवल कठिन शब्दों को बिना समझे रटना (Rote memorization without understanding)',
          'पाठ्य-पुस्तक के संदर्भ और नियमों की अनदेखी करना (Ignoring textual context and grammar rules)',
          'अप्रासंगिक नियमों को लागू करना (Applying unrelated rules)',
        ],
        correctIndex: 0,
        explanation: 'भाषा एवं साहित्य के इस अध्याय से व्याकरणिक नियमों की समझ और भाषाई अभिव्यक्ति में सुधार होता है।',
      },
      {
        id: 2,
        question: `इस पाठ्यांश (${topicName}) में भावार्थ अथवा व्याख्या करते समय किन बातों का ध्यान रखना आवश्यक है?`,
        options: [
          'प्रसंग, संदर्भ, मुख्य भाव एवं काव्य/गद्य सौंदर्य का संतुलित विश्लेषण (Balanced analysis of context and theme)',
          'मूल भाव को छोड़कर केवल शब्दार्थ लिखना (Writing word meanings while ignoring the central theme)',
          'बिना संदर्भ के मनगढ़ंत व्याख्या प्रस्तुत करना (Fabricating explanations without context)',
          'बोर्ड परीक्षा के उत्तर प्रारूप का पालन न करना (Not following standard board examination format)',
        ],
        correctIndex: 0,
        explanation: 'सटीक प्रसंग, केंद्रीय भाव और काव्य सौंदर्य का समावेश ही बोर्ड परीक्षा में पूर्ण अंक दिलाता है।',
      },
      {
        id: 3,
        question: `पाठ्यक्रम के अनुसार ${topicName} में प्रयुक्त भाषा-शैली और शब्द-सामर्थ्य का क्या महत्व है?`,
        options: [
          'यह अभिव्यक्ति को प्रभावी, परिष्कृत और परीक्षा के मानकों के अनुरूप बनाता है (Refines expression according to board standards)',
          'इसका परीक्षा अथवा दैनिक अभिव्यक्ति से कोई संबंध नहीं है (It has no connection with exams)',
          'यह केवल वैकल्पिक परियोजनाओं तक सीमित है (Limited only to optional projects)',
          'इससे वाक्य संरचना त्रुटिपूर्ण होती है (Causes errors in sentence construction)',
        ],
        correctIndex: 0,
        explanation: 'उचित शब्द-सामर्थ्य और सटीक व्याकरणिक संरचना से विद्यार्थी की भाषा दक्षता में प्रामाणिक वृद्धि होती है।',
      },
    ];
  }
  return [
    {
      id: 1,
      question: `What is the primary conceptual focus of "${topicName}" in the ${subject} syllabus?`,
      options: [
        `Mastering fundamental rules, derivations, and board-prescribed problem solving in ${subject}`,
        'Memorizing disconnected facts without conceptual reasoning',
        'Discarding official syllabus formulas and scoring steps',
        'Focusing on non-syllabus material',
      ],
      correctIndex: 0,
      explanation: `Mastering this unit establishes essential competencies and scoring fundamentals in ${subject}.`,
    },
    {
      id: 2,
      question: `Which methodology is recommended when analyzing concepts in ${topicName}?`,
      options: [
        'Step-by-step conceptual derivation aligned with board curriculum standards',
        'Skipping practice exercises and theoretical review',
        'Relying solely on external unverified summaries',
        'Leaving high-weightage sections unprepared for evaluations',
      ],
      correctIndex: 0,
      explanation: 'Structured derivation and step-by-step problem-solving guarantee comprehensive syllabus mastery.',
    },
    {
      id: 3,
      question: `How does mastering "${topicName}" benefit overall performance in ${subject}?`,
      options: [
        'It establishes essential prerequisites for subsequent advanced curriculum chapters',
        'It has zero connection to any exam questions or syllabus scoring criteria',
        'It only applies to optional extracurricular research projects',
        'It replaces the requirement to understand basic terminology',
      ],
      correctIndex: 0,
      explanation: 'Foundational mastery of this topic strengthens multi-concept analytical problem solving across the subject.',
    },
  ];
};\n\n"""
    text = text[:start_idx] + new_func + text[end_idx:]
    with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced getDynamicFallbackQuiz with language-aware questions")
else:
    print("Markers not found")

