import sys

with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace SELF_CHECK_QUIZ definition
idx_quiz_start = text.find('const SELF_CHECK_QUIZ: QuizQuestion[] = [')
idx_quiz_end = text.find('export const TopicStudyPage: React.FC = () => {')

if idx_quiz_start != -1 and idx_quiz_end != -1:
    new_quiz_def = '''const getDynamicFallbackQuiz = (subject: string, topicName: string): QuizQuestion[] => [
  {
    id: 1,
    question: `What is the primary conceptual focus of "${topicName}" in the ${subject} syllabus?`,
    options: [
      `Understanding core principles and foundational application in ${subject}`,
      'Memorizing unconnected numerical dates without conceptual context',
      'Discarding standard syllabus terminology and scoring conventions',
      'Focusing solely on unrelated historical chronologies',
    ],
    correctIndex: 0,
    explanation: `This unit builds foundational proficiency and key exam competencies in ${subject}.`,
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
];\n\n'''
    text = text[:idx_quiz_start] + new_quiz_def + text[idx_quiz_end:]
    print("Replaced quiz def")

# 2. Replace initial chatMessages state
old_chat = '''  // Chapter AI Tutor Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'user',
      text: 'Why did Akbar end the jizya tax?',
    },
    {
      id: '2',
      sender: 'bot',
      text: 'Great question! Akbar abolished the jizya tax in 1564 to establish his foundational policy of Sulh-i-Kul (universal peace) and remove discriminatory burdens between Hindu and Muslim subjects, consolidating an integrated imperial state.',
    },
  ]);'''

new_chat = '''  // Chapter AI Tutor Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);'''

if old_chat in text:
    text = text.replace(old_chat, new_chat, 1)
    print("Replaced chat state")

# 3. Dynamic welcoming message when topic is loaded
old_load = '''        if (isMounted) {
          setTopic(data);
          const prog = data.progress || data.user_progress;
          if (prog?.status === 'completed') {
            setIsCompleted(true);
          }
        }'''

new_load = '''        if (isMounted) {
          setTopic(data);
          const prog = data.progress || data.user_progress;
          if (prog?.status === 'completed') {
            setIsCompleted(true);
          }
          setChatMessages([
            {
              id: 'welcome',
              sender: 'bot',
              text: `Hello! I am your AI Tutor for ${data.subject_name || 'this subject'}. Ask me anything about ${data.title || 'this topic'} or any doubts from your syllabus!`,
            },
          ]);
        }'''

if old_load in text:
    text = text.replace(old_load, new_load, 1)
    print("Added dynamic tutor greeting")

# 4. Fallback in catch for chat messages
old_catch = '''      const fallbackMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: 'bot',
        text: `According to your CISCE ISC syllabus for this chapter, this key concept is evaluated through administrative and economic reform points.`,
      };'''

new_catch = '''      const fallbackMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: 'bot',
        text: `Based on the ${subjectName} curriculum for this chapter (${topicTitle}), focus on the foundational principles and structured exam definitions.`,
      };'''

if old_catch in text:
    text = text.replace(old_catch, new_catch, 1)
    print("Replaced catch text")

# 5. Dynamic fallback video
old_fallback_vid = '''  // Dynamic video ID derived from subject category if no explicit resource
  const fallbackVideoId = anyMatches(subjectName, ['math', 'account', 'calc'])
    ? '9bZkp7q19f0'
    : anyMatches(subjectName, ['sci', 'phys', 'chem', 'bio'])
    ? 'yE8rkG9Dw4s'
    : 'nbuM0aJjVgE';'''

new_fallback_vid = '''  // Dynamic video ID derived from subject category if no explicit resource
  const fallbackVideoId = anyMatches(subjectName, ['sanskrit', 'ruchira'])
    ? 'T6o6WkQ54pE'
    : anyMatches(subjectName, ['hindi'])
    ? 'qR812uE16kE'
    : anyMatches(subjectName, ['math', 'account', 'calc'])
    ? '9bZkp7q19f0'
    : anyMatches(subjectName, ['sci', 'phys', 'chem', 'bio'])
    ? 'yE8rkG9Dw4s'
    : anyMatches(subjectName, ['english', 'literature'])
    ? 'JULrwhkY6eM'
    : 'T6o6WkQ54pE';'''

if old_fallback_vid in text:
    text = text.replace(old_fallback_vid, new_fallback_vid, 1)
    print("Replaced fallback video logic")

# 6. Key points card ISC syllabus text
old_kp = '''                  {/* Key Points Card matching Design */}
                  <div className="key-points-card-clean">
                    <h3 className="key-points-title">Key points</h3>
                    <p className="key-points-desc">
                      {notesResource?.text_content ||
                        `Short notes for this chapter, matched to your ISC syllabus, appear here.`}
                    </p>
                  </div>'''

new_kp = '''                  {/* Key Points Card matching Design */}
                  <div className="key-points-card-clean">
                    <h3 className="key-points-title">Key points</h3>
                    <p className="key-points-desc">
                      {notesResource?.text_content ||
                        dynamicNotes?.summary ||
                        `Key study notes for ${topicTitle} (${subjectName}) aligned with your curriculum syllabus.`}
                    </p>
                  </div>'''

if old_kp in text:
    text = text.replace(old_kp, new_kp, 1)
    print("Replaced key points ISC syllabus text")

# 7. SELF_CHECK_QUIZ usage in quiz render
old_quiz_map = '''                    : SELF_CHECK_QUIZ
                  ).map((q, idx) => {'''

new_quiz_map = '''                    : getDynamicFallbackQuiz(subjectName, topicTitle)
                  ).map((q, idx) => {'''

if old_quiz_map in text:
    text = text.replace(old_quiz_map, new_quiz_map, 1)
    print("Replaced quiz map call")

with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated TopicStudyPage.tsx successfully!")

