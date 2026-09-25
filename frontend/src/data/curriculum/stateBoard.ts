import type { GradeCurriculumDefinition, StateBoardCurriculumManifest, SubjectItem } from './types';

export const INDIAN_STATES: string[] = [
  'Andhra Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Delhi',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Tamil Nadu',
  'Telangana',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
];

// Generic State Baseline — Explicitly labeled as provisional, NOT official state syllabus
const BASELINE_SECONDARY_SUBJECTS: SubjectItem[] = [
  {
    id: 'state-base-first-lang',
    name: 'First Language (Regional Language / Mother Tongue)',
    category: 'language',
    required: true,
    selectable: true,
    cssClass: 'subject-hindi',
  },
  {
    id: 'state-base-second-lang',
    name: 'Second Language (English / Hindi)',
    category: 'language',
    required: true,
    selectable: true,
    cssClass: 'subject-english',
  },
  {
    id: 'state-base-math',
    name: 'Mathematics',
    category: 'core',
    required: true,
    selectable: true,
    cssClass: 'subject-math',
  },
  {
    id: 'state-base-science',
    name: 'Science & Technology',
    category: 'core',
    required: true,
    selectable: true,
    cssClass: 'subject-chem',
  },
  {
    id: 'state-base-social-science',
    name: 'Social Sciences',
    category: 'core',
    required: true,
    selectable: true,
    cssClass: 'subject-bio',
  },
];

const BASELINE_SENIOR_SCIENCE: SubjectItem[] = [
  { id: 'state-base-sci-eng', name: 'English', category: 'language', required: true, selectable: true, cssClass: 'subject-english' },
  { id: 'state-base-sci-phy', name: 'Physics', category: 'elective', required: false, selectable: true, cssClass: 'subject-physics' },
  { id: 'state-base-sci-chem', name: 'Chemistry', category: 'elective', required: false, selectable: true, cssClass: 'subject-chem' },
  { id: 'state-base-sci-math', name: 'Mathematics', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
  { id: 'state-base-sci-bio', name: 'Biology', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'state-base-sci-it', name: 'Computer Science / Information Technology', category: 'skill', required: false, selectable: true, cssClass: 'subject-cs' },
];

const BASELINE_SENIOR_COMMERCE: SubjectItem[] = [
  { id: 'state-base-comm-eng', name: 'English', category: 'language', required: true, selectable: true, cssClass: 'subject-english' },
  { id: 'state-base-comm-acc', name: 'Accountancy', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
  { id: 'state-base-comm-comm', name: 'Commerce / Organisation of Commerce', category: 'elective', required: false, selectable: true, cssClass: 'subject-chem' },
  { id: 'state-base-comm-eco', name: 'Economics', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'state-base-comm-math', name: 'Secretarial Practice / Mathematics', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
];

const BASELINE_SENIOR_HUMANITIES: SubjectItem[] = [
  { id: 'state-base-hum-eng', name: 'English', category: 'language', required: true, selectable: true, cssClass: 'subject-english' },
  { id: 'state-base-hum-hist', name: 'History', category: 'elective', required: false, selectable: true, cssClass: 'subject-bio' },
  { id: 'state-base-hum-pol', name: 'Political Science', category: 'elective', required: false, selectable: true, cssClass: 'subject-physics' },
  { id: 'state-base-hum-geo', name: 'Geography', category: 'elective', required: false, selectable: true, cssClass: 'subject-chem' },
  { id: 'state-base-hum-soc', name: 'Sociology', category: 'elective', required: false, selectable: true, cssClass: 'subject-math' },
];

const GENERAL_STATE_BASELINE: Record<string, GradeCurriculumDefinition> = {
  'Class 6': { grade: 'Class 6', hasStreams: false, subjects: BASELINE_SECONDARY_SUBJECTS },
  'Class 7': { grade: 'Class 7', hasStreams: false, subjects: BASELINE_SECONDARY_SUBJECTS },
  'Class 8': { grade: 'Class 8', hasStreams: false, subjects: BASELINE_SECONDARY_SUBJECTS },
  'Class 9': { grade: 'Class 9', hasStreams: false, subjects: BASELINE_SECONDARY_SUBJECTS },
  'Class 10': { grade: 'Class 10', hasStreams: false, subjects: BASELINE_SECONDARY_SUBJECTS },
  'Class 11': {
    grade: 'Class 11',
    hasStreams: true,
    streams: {
      Science: BASELINE_SENIOR_SCIENCE,
      Commerce: BASELINE_SENIOR_COMMERCE,
      'Humanities / Arts': BASELINE_SENIOR_HUMANITIES,
      Other: [...BASELINE_SENIOR_SCIENCE.slice(0, 3), ...BASELINE_SENIOR_COMMERCE.slice(1, 3)],
    },
  },
  'Class 12': {
    grade: 'Class 12',
    hasStreams: true,
    streams: {
      Science: BASELINE_SENIOR_SCIENCE,
      Commerce: BASELINE_SENIOR_COMMERCE,
      'Humanities / Arts': BASELINE_SENIOR_HUMANITIES,
      Other: [...BASELINE_SENIOR_SCIENCE.slice(0, 3), ...BASELINE_SENIOR_COMMERCE.slice(1, 3)],
    },
  },
};

export const STATE_BOARD_CURRICULUM: StateBoardCurriculumManifest = {
  board: 'State Board',
  academicYear: '2026-27',
  sourceTitle: 'General State Baseline (Provisional / Pending Official State-Specific Manifests)',
  lastVerified: '2026-09-10',
  states: {},
  generalStateBaseline: GENERAL_STATE_BASELINE,
};
