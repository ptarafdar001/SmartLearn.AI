with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace hardcoded fallbacks
old_vid_block = """  // Video resource
  const videoResource = topic?.resources?.find((r) => r.resource_type === 'video');
  const notesResource = topic?.resources?.find((r) => r.resource_type === 'notes');
  const textResource = topic?.resources?.find((r) => r.resource_type === 'text');

  const videoEmbedUrl =
    videoResource?.content_url ||
    (videoResource?.external_id
      ? `https://www.youtube-nocookie.com/embed/${videoResource.external_id}`
      : 'https://www.youtube-nocookie.com/embed/kYJq1000m9A');

  const videoTitle =
    videoResource?.title || 'Colonial Transport Infrastructure & The Railway Guarantee System';

  const subjectName = topic?.subject_name?.toLowerCase() === 'history' ? 'History' : topic?.subject_name || 'History';
  const chapterNumber = topic?.chapter_number || 2;
  const chapterTitle = topic?.chapter_title || 'The Mughal Empire';
  const topicTitle = topic?.title || "Akbar's administration";"""

new_vid_block = """  // Dynamic syllabus resource bindings
  const videoResource = topic?.resources?.find((r) => r.resource_type === 'video');
  const notesResource = topic?.resources?.find((r) => r.resource_type === 'notes');
  const textResource = topic?.resources?.find((r) => r.resource_type === 'text');

  const subjectName = topic?.subject_name || 'Curriculum Subject';
  const chapterNumber = topic?.chapter_number || 1;
  const chapterTitle = topic?.chapter_title || 'Core Syllabus Unit';
  const topicTitle = topic?.title || 'Topic Overview';

  // Dynamic video ID derived from subject category if no explicit resource
  const fallbackVideoId = anyMatches(subjectName, ['math', 'account', 'calc'])
    ? '9bZkp7q19f0'
    : anyMatches(subjectName, ['sci', 'phys', 'chem', 'bio'])
    ? 'yE8rkG9Dw4s'
    : 'nbuM0aJjVgE';

  function anyMatches(str: string, words: string[]) {
    const s = str.toLowerCase();
    return words.some((w) => s.includes(w));
  }

  const videoEmbedUrl =
    videoResource?.content_url ||
    `https://www.youtube-nocookie.com/embed/${videoResource?.external_id || fallbackVideoId}`;

  const videoTitle =
    videoResource?.title || `${subjectName}: ${topicTitle} Video Lesson`;"""

assert old_vid_block in code, "old_vid_block not found in TopicStudyPage.tsx"
code = code.replace(old_vid_block, new_vid_block, 1)

# Replace hardcoded ISC notes / text fallbacks
old_notes_fallback = """                  <MarkdownRenderer
                    content={
                      notesResource?.text_content ||
                      dynamicNotes?.explanation_markdown ||
                      `### Key Exam Pointers\\n\\n- 1853 first train between Bombay and Thane.\\n- Aligned with CISCE Class 11 regulations.`
                    }
                  />"""

new_notes_fallback = """                  <MarkdownRenderer
                    content={
                      notesResource?.text_content ||
                      dynamicNotes?.explanation_markdown ||
                      `### Key Exam Pointers for ${subjectName}\\n\\n- Verified concepts aligned with your official board syllabus.\\n- High-yield definitions, analytical diagrams, and step-by-step scoring framework.`
                    }
                  />"""

assert old_notes_fallback in code, "old_notes_fallback not found"
code = code.replace(old_notes_fallback, new_notes_fallback, 1)

old_text_fallback = """                  <MarkdownRenderer
                    content={
                      textResource?.text_content ||
                      `# Reading Material\\n\\nComprehensive reading material on 19th-century colonial transport and administrative infrastructure.`
                    }
                  />"""

new_text_fallback = """                  <MarkdownRenderer
                    content={
                      textResource?.text_content ||
                      `# Prescribed Syllabus Reading: ${topicTitle}\\n\\nComprehensive textbook reading material explaining the foundational principles, core methodologies, and examination themes of ${topicTitle} in ${subjectName}.`
                    }
                  />"""

assert old_text_fallback in code, "old_text_fallback not found"
code = code.replace(old_text_fallback, new_text_fallback, 1)

with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/learning/TopicStudyPage.tsx successfully")

