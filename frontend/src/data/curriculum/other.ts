import type { BoardCurriculumManifest, SubjectItem } from './types';

const OTHER_FLEXIBLE_SECONDARY: SubjectItem[] = [
  { id: 'other-sec-eng', name: 'English Language & Literature', category: 'language', required: false, selectable: true, cssClass: 'subject-english' },
  { id: 'other-sec-math', name: 'Mathematics', category: 'core', required: false, selectable: true, cssClass: 'subject-math' },
  { id: 'other-sec-sci', name: 'General Science / Integrated Science', category: 'core', required: false, selectable: true, cssClass: 'subject-chem' },
  { id: 'other-sec-soc', name: 'Social Studies / Humanities', category: 'core', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'other-sec-lang', name: 'World / Regional Language', category: 'language', required: false, selectable: true, cssClass: 'subject-hindi' },
  { id: 'other-sec-ict', name: 'Computer Science / ICT', category: 'skill', required: false, selectable: true, cssClass: 'subject-cs' },
];

const OTHER_SENIOR_SCIENCE: SubjectItem[] = [
  { id: 'other-sr-eng', name: 'English', category: 'language', required: false, selectable: true, cssClass: 'subject-english' },
  { id: 'other-sr-phy', name: 'Physics', category: 'elective', required: false, selectable: true, cssClass: 'subject-physics' },
  { id: 'other-sr-chem', name: 'Chemistry', category: 'elective', required: false, selectable: true, cssClass: 'subject-chem' },
  { id: 'other-sr-math', name: 'Mathematics', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
  { id: 'other-sr-bio', name: 'Biology / Life Sciences', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'other-sr-cs', name: 'Computer Science', category: 'elective', required: false, selectable: true, cssClass: 'subject-cs' },
];

const OTHER_SENIOR_COMMERCE: SubjectItem[] = [
  { id: 'other-sr-eng', name: 'English', category: 'language', required: false, selectable: true, cssClass: 'subject-english' },
  { id: 'other-sr-acc', name: 'Accounting', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
  { id: 'other-sr-bus', name: 'Business Management', category: 'elective', required: false, selectable: true, cssClass: 'subject-chem' },
  { id: 'other-sr-eco', name: 'Economics', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'other-sr-math', name: 'Mathematics', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
];

const OTHER_SENIOR_HUMANITIES: SubjectItem[] = [
  { id: 'other-sr-eng', name: 'English', category: 'language', required: false, selectable: true, cssClass: 'subject-english' },
  { id: 'other-sr-hist', name: 'World History', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'other-sr-pol', name: 'Global Politics / Political Science', category: 'elective', required: false, selectable: true, cssClass: 'subject-physics' },
  { id: 'other-sr-psych', name: 'Psychology', category: 'elective', required: false, selectable: true, cssClass: 'subject-cs' },
  { id: 'other-sr-soc', name: 'Sociology', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
  { id: 'other-sr-eco', name: 'Economics', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
];

const OTHER_SENIOR_OTHER: SubjectItem[] = [
  ...OTHER_SENIOR_SCIENCE.slice(0, 3),
  ...OTHER_SENIOR_COMMERCE.slice(1, 3),
  ...OTHER_SENIOR_HUMANITIES.slice(1, 3),
];

export const OTHER_CURRICULUM: BoardCurriculumManifest = {
  board: 'Other',
  academicYear: '2026-27',
  sourceUrl: 'https://smartlearn.ai',
  sourceTitle: 'SmartLearn Flexible International / Non-Standard Baseline',
  lastVerified: '2026-09-10',
  grades: {
    'Class 6': { grade: 'Class 6', hasStreams: false, subjects: OTHER_FLEXIBLE_SECONDARY },
    'Class 7': { grade: 'Class 7', hasStreams: false, subjects: OTHER_FLEXIBLE_SECONDARY },
    'Class 8': { grade: 'Class 8', hasStreams: false, subjects: OTHER_FLEXIBLE_SECONDARY },
    'Class 9': { grade: 'Class 9', hasStreams: false, subjects: OTHER_FLEXIBLE_SECONDARY },
    'Class 10': { grade: 'Class 10', hasStreams: false, subjects: OTHER_FLEXIBLE_SECONDARY },
    'Class 11': {
      grade: 'Class 11',
      hasStreams: true,
      streams: {
        Science: OTHER_SENIOR_SCIENCE,
        Commerce: OTHER_SENIOR_COMMERCE,
        'Humanities / Arts': OTHER_SENIOR_HUMANITIES,
        Other: OTHER_SENIOR_OTHER,
      },
    },
    'Class 12': {
      grade: 'Class 12',
      hasStreams: true,
      streams: {
        Science: OTHER_SENIOR_SCIENCE,
        Commerce: OTHER_SENIOR_COMMERCE,
        'Humanities / Arts': OTHER_SENIOR_HUMANITIES,
        Other: OTHER_SENIOR_OTHER,
      },
    },
  },
};
