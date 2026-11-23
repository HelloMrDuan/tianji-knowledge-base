/**
 * TJ-0422 phase 2 slice A: session-level shared state for the dayun
 * timeline <-> yearly linkage.
 *
 * What lives here (in-memory only, never persisted):
 * - the full bazi-profile dayun presentation (both methods, 8 entries
 *   each) returned by the last bazi-profile calculation in this tab;
 * - the selected dayun period index and the selected dayun method;
 * - a one-shot pending year request (a year link clicked on the
 *   timeline) and a one-shot pending dayun return (the "back to my
 *   dayun" link on the yearly page).
 *
 * What does NOT live here:
 * - the traditional role: it is never stored, defaulted, inferred, or
 *   put in a URL. It lives only inside the dayun presentation the
 *   backend returned for an explicitly selected role.
 * - birth data: still the single localStorage key
 *   tianji.profile.birth.v1 owned by birthProfile.ts.
 * - the target year: still the shared key owned by targetYear.ts
 *   (tianji.scenario.target-year.v1). getSelectedYear/setSelectedYear
 *   below are thin wrappers over that key, so every page that reads
 *   the key stays in sync.
 *
 * No dayun, year, or role value is ever computed here: the timeline
 * and the yearly location only read fields the backend returned
 * (period_index / ganzhi / stem / branch /
 * ten_god_relative_to_natal_day_stem / state / start_interval with
 * earliest / latest). The two pure helpers below only compare those
 * returned intervals against a date or a calendar year; they never
 * derive a ganzhi, a ten-god, an age, or a single handover date.
 */

import {
  readSavedTargetYear,
  saveTargetYear,
  isValidTargetYear,
} from "./targetYear";

export type DayunMethod = "sanming" | "shenfeng";
export const DAYUN_METHODS: DayunMethod[] = ["sanming", "shenfeng"];
export const DEFAULT_DAYUN_METHOD: DayunMethod = "sanming";

/** One entry of a method's 8-period dayun presentation (exact backend keys). */
export type DayunEntry = {
  period_index: number;
  ganzhi: string;
  stem: string;
  branch: string;
  ten_god_relative_to_natal_day_stem: string;
  state: "interval" | "not_provided" | "unresolved";
  start_interval: {
    earliest: string;
    latest: string;
    max_inclusive?: boolean;
    [key: string]: unknown;
  } | null;
  [key: string]: unknown;
};

/** One method view of the dayun presentation (exact backend shape). */
export type DayunMethodView = {
  method: string;
  status: string;
  natal: Record<string, any>;
  direction: Record<string, any>;
  duration: Record<string, any>;
  entries: DayunEntry[];
  notices: Array<Record<string, any>>;
  sources: any;
  [key: string]: unknown;
};

/** The full bazi-profile dayun presentation (both methods). */
export type DayunPresentation = {
  variant?: string;
  status?: string;
  role?: Record<string, any>;
  methods: Record<string, DayunMethodView>;
  method_options?: Record<string, any>;
  evidence?: Record<string, any>;
  scope?: string[];
  limitations?: string[];
  [key: string]: unknown;
};

/**
 * Fixed stem/branch -> element display mapping. This is a character
 * lookup for display only ("辛" is shown with "金"); it derives no
 * judgment, no ten-god, and no relation.
 */
export const STEM_ELEMENTS: Record<string, string> = {
  甲: "木", 乙: "木", 丙: "火", 丁: "火", 戊: "土",
  己: "土", 庚: "金", 辛: "金", 壬: "水", 癸: "水",
};
export const BRANCH_ELEMENTS: Record<string, string> = {
  子: "水", 丑: "土", 寅: "木", 卯: "木", 辰: "土", 巳: "火",
  午: "火", 未: "土", 申: "金", 酉: "金", 戌: "土", 亥: "水",
};

// ---------------------------------------------------------------------------
// Session state (module memory only).
// ---------------------------------------------------------------------------

let dayunPresentation: DayunPresentation | null = null;
let selectedPeriodIndex: number | null = null;
let selectedDayunMethod: DayunMethod = DEFAULT_DAYUN_METHOD;
let pendingYearRequest: number | null = null;
let pendingDayunReturn = false;

const listeners = new Set<() => void>();
function notify(): void {
  listeners.forEach((fn) => {
    try {
      fn();
    } catch {
      // A failing subscriber must not break state updates.
    }
  });
}

/**
 * Subscribe to any shared-state change. Returns an unsubscribe function.
 * Listeners are also notified when the shared target-year key changes
 * in another tab (storage event).
 */
export function subscribe(fn: () => void): () => void {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

if (typeof window !== "undefined") {
  window.addEventListener("storage", () => notify());
}

/** The full dayun presentation from the last bazi-profile calculation, or null. */
export function getDayunPresentation(): DayunPresentation | null {
  return dayunPresentation;
}

/** Store (or clear with null) the dayun presentation. Session memory only. */
export function setDayunPresentation(presentation: DayunPresentation | null): void {
  dayunPresentation = presentation;
  if (presentation === null) selectedPeriodIndex = null;
  notify();
}

/** The period the user last selected on the timeline, or null. */
export function getSelectedPeriodIndex(): number | null {
  return selectedPeriodIndex;
}

/** Select (or clear with null) a timeline period. Session memory only. */
export function setSelectedPeriodIndex(periodIndex: number | null): void {
  selectedPeriodIndex = periodIndex;
  notify();
}

/** The method tab last selected on the bazi page ("sanming" by default). */
export function getSelectedDayunMethod(): DayunMethod {
  return selectedDayunMethod;
}

/** Remember the selected method tab. Session memory only. */
export function setSelectedDayunMethod(method: DayunMethod): void {
  if (method !== "sanming" && method !== "shenfeng") return;
  selectedDayunMethod = method;
  notify();
}

/** The shared target year (same key targetYear.ts owns). */
export function getSelectedYear(): number {
  return readSavedTargetYear();
}

/** Write the shared target year. Throws on an out-of-range year. */
export function setSelectedYear(year: number): void {
  if (!isValidTargetYear(year)) {
    throw new Error("请选择 1901 至 2098 年的公历年份");
  }
  saveTargetYear(year);
  notify();
}

/**
 * Request the yearly page for `year`: writes the shared year key and
 * arms a one-shot flag so the yearly page auto-loads that year on
 * arrival instead of waiting for another submit.
 */
export function requestYearView(year: number): void {
  setSelectedYear(year);
  pendingYearRequest = year;
  notify();
}

/** Consume the one-shot pending year request, if any. */
export function consumePendingYearRequest(): number | null {
  const year = pendingYearRequest;
  pendingYearRequest = null;
  return year;
}

/**
 * Request a return to the bazi timeline for `periodIndex`: selects the
 * period and arms a one-shot flag so the bazi page scrolls to the
 * timeline on arrival.
 */
export function requestDayunReturn(periodIndex: number): void {
  selectedPeriodIndex = periodIndex;
  pendingDayunReturn = true;
  notify();
}

/** Consume the one-shot pending dayun-return flag. */
export function consumePendingDayunReturn(): boolean {
  const pending = pendingDayunReturn;
  pendingDayunReturn = false;
  return pending;
}

// ---------------------------------------------------------------------------
// Pure location helpers (only compare backend-returned intervals).
// ---------------------------------------------------------------------------

function parseInstant(value: string | undefined | null): number | null {
  if (typeof value !== "string" || !value) return null;
  const ms = Date.parse(value);
  return Number.isNaN(ms) ? null : ms;
}

function intervalOf(entry: DayunEntry): { earliest: number; latest: number } | null {
  if (entry.state !== "interval" || !entry.start_interval) return null;
  const earliest = parseInstant(entry.start_interval.earliest);
  const latest = parseInstant(entry.start_interval.latest);
  if (earliest === null || latest === null) return null;
  return { earliest, latest };
}

function sortedEntries(view: DayunMethodView | undefined): DayunEntry[] {
  if (!view || !Array.isArray(view.entries)) return [];
  return [...view.entries].sort((a, b) => a.period_index - b.period_index);
}

export type CurrentPeriodLocation =
  | { status: "current"; periodIndex: number; ganzhi: string }
  | {
      status: "ambiguous";
      fromPeriodIndex: number | null;
      toPeriodIndex: number;
      fromGanzhi: string | null;
      toGanzhi: string;
    }
  | { status: "before_first" }
  | { status: "unknown" };

/**
 * Which period `today` falls in, from the returned start intervals only.
 * - inside a start interval [earliest, latest): "ambiguous" (the
 *   handover may be happening; no forced归属).
 * - after an interval's latest and before the next interval's earliest:
 *   "current".
 * - before the first interval's earliest: "before_first".
 * - the next period's interval is not provided, or no interval can be
 *   parsed: "unknown" (never guessed).
 */
export function locateCurrentPeriod(
  presentation: DayunPresentation | null,
  method: DayunMethod,
  today: Date = new Date(),
): CurrentPeriodLocation {
  const entries = sortedEntries(presentation?.methods[method]);
  if (entries.length === 0) return { status: "unknown" };
  const now = today.getTime();
  const intervals = entries.map((entry) => ({ entry, interval: intervalOf(entry) }));

  for (let i = 0; i < intervals.length; i += 1) {
    const { entry, interval } = intervals[i];
    if (!interval) continue;
    if (now >= interval.earliest && now < interval.latest) {
      const prev = intervals
        .slice(0, i)
        .reverse()
        .find((row) => row.interval !== null);
      return {
        status: "ambiguous",
        fromPeriodIndex: prev ? prev.entry.period_index : null,
        toPeriodIndex: entry.period_index,
        fromGanzhi: prev ? prev.entry.ganzhi : null,
        toGanzhi: entry.ganzhi,
      };
    }
  }

  const started = intervals.filter(
    (row): row is { entry: DayunEntry; interval: { earliest: number; latest: number } } =>
      row.interval !== null && row.interval.latest <= now,
  );
  if (started.length === 0) {
    const first = intervals.find((row) => row.interval !== null);
    if (first && first.interval && now < first.interval.earliest) return { status: "before_first" };
    return { status: "unknown" };
  }
  const candidate = started[started.length - 1];
  const candidateIndex = intervals.findIndex((row) => row.entry === candidate.entry);
  const next = intervals[candidateIndex + 1];
  if (!next) return { status: "current", periodIndex: candidate.entry.period_index, ganzhi: candidate.entry.ganzhi };
  if (!next.interval) return { status: "unknown" };
  if (now < next.interval.earliest) {
    return { status: "current", periodIndex: candidate.entry.period_index, ganzhi: candidate.entry.ganzhi };
  }
  return { status: "unknown" };
}

export type YearDayunLocation =
  | {
      status: "located";
      method: DayunMethod;
      periodIndex: number;
      ganzhi: string;
      tenGod: string;
    }
  | {
      status: "ambiguous";
      method: DayunMethod;
      fromPeriodIndex: number | null;
      toPeriodIndex: number;
      fromGanzhi: string | null;
      toGanzhi: string;
    }
  | { status: "before_first"; method: DayunMethod }
  | {
      status: "not_provided";
      method: DayunMethod;
      lastKnownPeriodIndex: number;
      lastKnownGanzhi: string;
    }
  | { status: "unresolved"; method: DayunMethod }
  | { status: "no_presentation" };

/**
 * Which period calendar year `year` falls in, from the returned start
 * intervals only. A year overlapped by a start interval is "ambiguous"
 * (the handover happens inside that year; no unique归属 is forged).
 * A year after the last known interval whose next period has no
 * interval is "not_provided". A year before the first interval is
 * "before_first". The last period has no end: a year after its
 * interval, with no later entry at all, is "located" in it.
 */
export function locateYearInDayun(
  presentation: DayunPresentation | null,
  method: DayunMethod,
  year: number,
): YearDayunLocation {
  if (!presentation) return { status: "no_presentation" };
  const view = presentation.methods[method];
  if (!view) return { status: "no_presentation" };
  if (view.status === "unresolved") return { status: "unresolved", method };
  const entries = sortedEntries(view);
  if (entries.length === 0) return { status: "unresolved", method };

  const yearStart = new Date(year, 0, 1).getTime();
  const yearEnd = new Date(year + 1, 0, 1).getTime();
  const intervals = entries.map((entry) => ({ entry, interval: intervalOf(entry) }));

  for (let i = 0; i < intervals.length; i += 1) {
    const { entry, interval } = intervals[i];
    if (!interval) continue;
    if (interval.earliest < yearEnd && interval.latest > yearStart) {
      const prev = intervals
        .slice(0, i)
        .reverse()
        .find((row) => row.interval !== null);
      return {
        status: "ambiguous",
        method,
        fromPeriodIndex: prev ? prev.entry.period_index : null,
        toPeriodIndex: entry.period_index,
        fromGanzhi: prev ? prev.entry.ganzhi : null,
        toGanzhi: entry.ganzhi,
      };
    }
  }

  const started = intervals.filter(
    (row): row is { entry: DayunEntry; interval: { earliest: number; latest: number } } =>
      row.interval !== null && row.interval.latest <= yearStart,
  );
  if (started.length === 0) {
    const first = intervals.find((row) => row.interval !== null);
    if (first && first.interval && first.interval.earliest >= yearEnd) return { status: "before_first", method };
    return { status: "unresolved", method };
  }
  const candidate = started[started.length - 1];
  const candidateIndex = intervals.findIndex((row) => row.entry === candidate.entry);
  const next = intervals[candidateIndex + 1];
  if (!next) {
    return {
      status: "located",
      method,
      periodIndex: candidate.entry.period_index,
      ganzhi: candidate.entry.ganzhi,
      tenGod: candidate.entry.ten_god_relative_to_natal_day_stem,
    };
  }
  if (!next.interval) {
    return {
      status: "not_provided",
      method,
      lastKnownPeriodIndex: candidate.entry.period_index,
      lastKnownGanzhi: candidate.entry.ganzhi,
    };
  }
  if (next.interval.earliest >= yearEnd) {
    return {
      status: "located",
      method,
      periodIndex: candidate.entry.period_index,
      ganzhi: candidate.entry.ganzhi,
      tenGod: candidate.entry.ten_god_relative_to_natal_day_stem,
    };
  }
  return { status: "unresolved", method };
}
