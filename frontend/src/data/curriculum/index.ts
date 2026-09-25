import type {
  BoardCurriculumManifest,
  CurriculumQuery,
  CurriculumResult,
  SubjectItem,
} from './types';
import { CBSE_CURRICULUM } from './cbse';
import { ICSE_CURRICULUM } from './icse';
import { ISC_CURRICULUM } from './isc';
import { STATE_BOARD_CURRICULUM, INDIAN_STATES } from './stateBoard';
import { OTHER_CURRICULUM } from './other';

export * from './types';
export { INDIAN_STATES };

const REGULAR_BOARD_REGISTRY: Record<string, BoardCurriculumManifest> = {
  CBSE: CBSE_CURRICULUM,
  ICSE: ICSE_CURRICULUM,
  ISC: ISC_CURRICULUM,
  Other: OTHER_CURRICULUM,
};

/**
 * Standard stream names supported in SmartLearn UI for Classes 11 & 12
 */
export const SENIOR_SECONDARY_STREAMS = [
  'Science',
  'Commerce',
  'Humanities / Arts',
  'Other',
];

/**
 * Main curriculum resolution engine
 * Resolves available subjects strictly from verified board manifests
 */
export function getCurriculumSubjects(query: CurriculumQuery): CurriculumResult {
  const { board, grade, stream, state } = query;

  // 1. Validate board existence
  if (!board) {
    return {
      isSupported: false,
      board: '',
      grade: grade || '',
      subjects: [],
      hasStreams: false,
      notice: 'No education board specified.',
    };
  }

  // 2. Handle State Board
  if (board === 'State Board') {
    const stateManifest = STATE_BOARD_CURRICULUM;
    const gradeDef = stateManifest.generalStateBaseline[grade];

    if (!gradeDef) {
      return {
        isSupported: false,
        board,
        grade,
        state: state || null,
        subjects: [],
        hasStreams: false,
        notice: `Grade ${grade} is not currently configured for State Board.`,
      };
    }

    if (gradeDef.hasStreams) {
      if (!stream) {
        return {
          isSupported: true,
          board,
          grade,
          state: state || null,
          subjects: [],
          hasStreams: true,
          availableStreams: Object.keys(gradeDef.streams || {}),
          notice: 'Please select an academic stream.',
        };
      }

      const streamSubjects = gradeDef.streams?.[stream] || [];
      return {
        isSupported: streamSubjects.length > 0,
        board,
        grade,
        stream,
        state: state || null,
        subjects: streamSubjects,
        hasStreams: true,
        availableStreams: Object.keys(gradeDef.streams || {}),
        notice:
          'Using General State Baseline (provisional). Specific state curriculum manifest pending verification.',
      };
    }

    // Classes 6-10 (No stream)
    return {
      isSupported: true,
      board,
      grade,
      state: state || null,
      subjects: gradeDef.subjects || [],
      hasStreams: false,
      notice:
        'Using General State Baseline (provisional). Specific state curriculum manifest pending verification.',
    };
  }

  // 3. Handle Regular Boards (CBSE, ICSE, ISC, Other)
  const manifest = REGULAR_BOARD_REGISTRY[board];
  if (!manifest) {
    return {
      isSupported: false,
      board,
      grade,
      subjects: [],
      hasStreams: false,
      notice: `Board "${board}" is not recognized by the curriculum registry.`,
    };
  }

  const gradeDef = manifest.grades[grade];
  if (!gradeDef) {
    return {
      isSupported: false,
      board,
      grade,
      subjects: [],
      hasStreams: false,
      notice: `Grade "${grade}" is not offered under ${board}.`,
    };
  }

  // 4. Senior Secondary (Classes 11 & 12) — Stream dependent
  if (gradeDef.hasStreams) {
    const availableStreams = Object.keys(gradeDef.streams || {});

    if (!stream) {
      return {
        isSupported: true,
        board,
        grade,
        subjects: [],
        hasStreams: true,
        availableStreams,
        notice: 'Please select your academic stream.',
      };
    }

    const streamSubjects = gradeDef.streams?.[stream];
    if (!streamSubjects || streamSubjects.length === 0) {
      return {
        isSupported: false,
        board,
        grade,
        stream,
        subjects: [],
        hasStreams: true,
        availableStreams,
        notice: `Stream "${stream}" is not available for ${board} ${grade}.`,
      };
    }

    return {
      isSupported: true,
      board,
      grade,
      stream,
      subjects: streamSubjects,
      hasStreams: true,
      availableStreams,
    };
  }

  // 5. Secondary & Middle Stage (Classes 6–10) — No stream
  return {
    isSupported: true,
    board,
    grade,
    stream: null,
    subjects: gradeDef.subjects || [],
    hasStreams: false,
  };
}

/**
 * Check whether a prospective subject selection conflicts with existing selections
 */
export function checkMutualExclusion(
  subjectId: string,
  selectedSubjectIds: string[],
  availableSubjects: SubjectItem[]
): string | null {
  const target = availableSubjects.find((s) => s.id === subjectId);
  if (!target || !target.mutuallyExclusiveWith) return null;

  for (const exclusiveId of target.mutuallyExclusiveWith) {
    if (selectedSubjectIds.includes(exclusiveId)) {
      const conflicting = availableSubjects.find((s) => s.id === exclusiveId);
      return `Cannot select "${target.name}" together with "${conflicting?.name || exclusiveId}".`;
    }
  }

  return null;
}
