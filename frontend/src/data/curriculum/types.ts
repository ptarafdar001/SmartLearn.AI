/**
 * SmartLearn.AI Curriculum Data Types
 * Strongly typed definitions for board-level curriculum manifests,
 * subject items, combination restrictions, and query parameters.
 */

export type SubjectCategory = 'core' | 'language' | 'elective' | 'skill';

export interface SubjectItem {
  id: string;
  code?: string;
  name: string;
  category: SubjectCategory;
  required?: boolean;
  selectable?: boolean;
  mutuallyExclusiveWith?: string[];
  cssClass?: string;
  sourceUrl?: string;
  sourceTitle?: string;
}

export interface GradeCurriculumDefinition {
  grade: string;
  hasStreams: boolean;
  /** Populated for Classes 6-10 where stream does not apply */
  subjects?: SubjectItem[];
  /** Populated for Classes 11-12 where subjects depend on selected stream */
  streams?: Record<string, SubjectItem[]>;
}

export interface BoardCurriculumManifest {
  board: string;
  academicYear: string;
  sourceUrl: string;
  sourceTitle: string;
  lastVerified: string;
  grades: Record<string, GradeCurriculumDefinition>;
}

export interface StateBoardCurriculumManifest {
  board: 'State Board';
  academicYear: string;
  sourceTitle: string;
  lastVerified: string;
  states: Record<string, {
    stateName: string;
    grades: Record<string, GradeCurriculumDefinition>;
  }>;
  generalStateBaseline: Record<string, GradeCurriculumDefinition>;
}

export interface CurriculumQuery {
  board: string;
  grade: string;
  stream?: string | null;
  state?: string | null;
}

export interface CurriculumResult {
  isSupported: boolean;
  board: string;
  grade: string;
  stream?: string | null;
  state?: string | null;
  subjects: SubjectItem[];
  hasStreams: boolean;
  availableStreams?: string[];
  notice?: string;
}
