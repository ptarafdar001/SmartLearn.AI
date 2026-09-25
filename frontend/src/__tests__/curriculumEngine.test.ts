import { describe, it, expect } from 'vitest';
import {
  getCurriculumSubjects,
  checkMutualExclusion,
  INDIAN_STATES,
} from '../data/curriculum';

describe('Curriculum Engine & Selector (Phase 6B Curriculum Architecture)', () => {
  // 1. CBSE Class 6
  it('1. Resolves CBSE Class 6 curriculum (no stream required)', () => {
    const res = getCurriculumSubjects({ board: 'CBSE', grade: 'Class 6' });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(false);
    expect(res.subjects.length).toBeGreaterThanOrEqual(5);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('Mathematics');
    expect(names).toContain('Science');
    expect(names).toContain('Social Science');
    expect(names).toContain('English');
  });

  // 2. CBSE Class 9
  it('2. Resolves CBSE Class 9 curriculum with core, languages, and skill subjects', () => {
    const res = getCurriculumSubjects({ board: 'CBSE', grade: 'Class 9' });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(false);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('Science');
    expect(names).toContain('Social Science');
    expect(names).toContain('Mathematics Standard');
    expect(names).toContain('Mathematics Basic');
    expect(names).toContain('Artificial Intelligence');
  });

  // 3. CBSE Class 10
  it('3. Resolves CBSE Class 10 with verified subject codes', () => {
    const res = getCurriculumSubjects({ board: 'CBSE', grade: 'Class 10' });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(false);

    const mathStd = res.subjects.find((s) => s.id === 'cbse-10-041-math-std');
    expect(mathStd).toBeDefined();
    expect(mathStd?.code).toBe('041');

    const mathBasic = res.subjects.find((s) => s.id === 'cbse-10-241-math-basic');
    expect(mathBasic).toBeDefined();
    expect(mathBasic?.code).toBe('241');
  });

  // 4. CBSE Class 11 Science
  it('4. Resolves CBSE Class 11 Science curriculum with senior secondary electives', () => {
    const res = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 11',
      stream: 'Science',
    });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(true);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('Physics');
    expect(names).toContain('Chemistry');
    expect(names).toContain('Mathematics');
    expect(names).toContain('Biology');
    expect(names).toContain('Computer Science');
    expect(names).toContain('English Core');
  });

  // 5. CBSE Class 11 Commerce
  it('5. Resolves CBSE Class 11 Commerce curriculum with Accountancy, Business Studies, Economics', () => {
    const res = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 11',
      stream: 'Commerce',
    });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(true);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('Accountancy');
    expect(names).toContain('Business Studies');
    expect(names).toContain('Economics');
    expect(names).toContain('Informatics Practices');
    // Ensure Science-specific subjects are not in Commerce
    expect(names).not.toContain('Physics');
    expect(names).not.toContain('Chemistry');
  });

  // 6. CBSE Class 11 Humanities
  it('6. Resolves CBSE Class 11 Humanities curriculum with History, Political Science, Geography', () => {
    const res = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 11',
      stream: 'Humanities / Arts',
    });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(true);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('History');
    expect(names).toContain('Political Science');
    expect(names).toContain('Geography');
    expect(names).toContain('Psychology');
    expect(names).toContain('Sociology');
    // Ensure Commerce/Science-specific subjects are not in Humanities
    expect(names).not.toContain('Accountancy');
    expect(names).not.toContain('Physics');
  });

  // 7. CBSE Class 12
  it('7. Resolves CBSE Class 12 curriculum consistently with Class 11 composite structure', () => {
    const res = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 12',
      stream: 'Science',
    });
    expect(res.isSupported).toBe(true);
    expect(res.subjects.some((s) => s.name === 'Physics')).toBe(true);
  });

  // 8. ICSE Class 10
  it('8. Resolves ICSE Class 10 with Group I, Group II, and Group III subjects', () => {
    const res = getCurriculumSubjects({ board: 'ICSE', grade: 'Class 10' });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(false);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('English');
    expect(names).toContain('History, Civics and Geography');
    expect(names).toContain('Mathematics');
    expect(names).toContain('Science (Physics, Chemistry, Biology)');
    expect(names).toContain('Commercial Studies');
    expect(names).toContain('Computer Applications');
  });

  // 9. ISC Class 11
  it('9. Resolves ISC Class 11 with compulsory English and stream electives', () => {
    const res = getCurriculumSubjects({
      board: 'ISC',
      grade: 'Class 11',
      stream: 'Commerce',
    });
    expect(res.isSupported).toBe(true);
    expect(res.hasStreams).toBe(true);

    const names = res.subjects.map((s) => s.name);
    expect(names).toContain('English');
    expect(names).toContain('Accounts');
    expect(names).toContain('Commerce');
    expect(names).toContain('Business Studies');
    expect(names).toContain('Economics');
  });

  // 10. State Board without state
  it('10. Resolves State Board using General State Baseline and provisional notice', () => {
    const res = getCurriculumSubjects({
      board: 'State Board',
      grade: 'Class 10',
    });
    expect(res.isSupported).toBe(true);
    expect(res.notice).toContain('General State Baseline');
    expect(res.subjects.some((s) => s.name === 'Mathematics')).toBe(true);
  });

  // 11. State Board with state
  it('11. Accepts state parameter for State Board curriculum and preserves state context', () => {
    const res = getCurriculumSubjects({
      board: 'State Board',
      grade: 'Class 10',
      state: 'Maharashtra',
    });
    expect(res.isSupported).toBe(true);
    expect(res.state).toBe('Maharashtra');
    expect(res.subjects.length).toBeGreaterThan(0);
    expect(INDIAN_STATES).toContain('Maharashtra');
  });

  // 12. Other curriculum
  it('12. Resolves Other flexible curriculum for international / non-standard students', () => {
    const res = getCurriculumSubjects({
      board: 'Other',
      grade: 'Class 10',
    });
    expect(res.isSupported).toBe(true);
    expect(res.subjects.some((s) => s.name.includes('Integrated Science') || s.name.includes('Science'))).toBe(true);
  });

  // 13. Stream switching
  it('13. Switching stream changes available subjects completely without caching stale tracks', () => {
    const sciRes = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 11',
      stream: 'Science',
    });
    const commRes = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 11',
      stream: 'Commerce',
    });

    const sciIds = sciRes.subjects.map((s) => s.id);
    const commIds = commRes.subjects.map((s) => s.id);

    expect(sciIds).toContain('cbse-11-042-physics');
    expect(commIds).not.toContain('cbse-11-042-physics');

    expect(commIds).toContain('cbse-11-055-accountancy');
    expect(sciIds).not.toContain('cbse-11-055-accountancy');
  });

  // 14. Mutual exclusion
  it('14. Enforces mutual exclusion rules accurately', () => {
    const res = getCurriculumSubjects({
      board: 'CBSE',
      grade: 'Class 10',
    });

    // Conflict between Mathematics Standard and Mathematics Basic
    const conflict = checkMutualExclusion(
      'cbse-10-241-math-basic',
      ['cbse-10-041-math-std'],
      res.subjects
    );
    expect(conflict).toContain('Cannot select "Mathematics Basic" together with "Mathematics Standard".');

    // No conflict with unrelated subject
    const noConflict = checkMutualExclusion(
      'cbse-10-086-science',
      ['cbse-10-041-math-std'],
      res.subjects
    );
    expect(noConflict).toBeNull();
  });

  // 15. No cross-board leakage
  it('15. Strictly isolates boards and prevents cross-board subject leakage', () => {
    const cbseRes = getCurriculumSubjects({ board: 'CBSE', grade: 'Class 10' });
    const icseRes = getCurriculumSubjects({ board: 'ICSE', grade: 'Class 10' });

    const cbseIds = cbseRes.subjects.map((s) => s.id);
    const icseIds = icseRes.subjects.map((s) => s.id);

    for (const id of cbseIds) {
      expect(id.startsWith('cbse-')).toBe(true);
      expect(icseIds).not.toContain(id);
    }

    for (const id of icseIds) {
      expect(id.startsWith('icse-')).toBe(true);
      expect(cbseIds).not.toContain(id);
    }
  });
});
