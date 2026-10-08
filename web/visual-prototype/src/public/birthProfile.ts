/** One browser-local birth profile across real consumer scenario pages.
 * Never transmitted except as part of the user's explicit calculation request.
 */
const KEY = "tianji.profile.birth.v1";

export type BirthProfile = { date: string; time: string };

const EMPTY_PROFILE: BirthProfile = { date: "", time: "" };

export function readSavedBirthProfile(): BirthProfile {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...EMPTY_PROFILE };
    const parsed: unknown = JSON.parse(raw);
    if (typeof parsed !== "object" || parsed === null) return { ...EMPTY_PROFILE };
    const record = parsed as Record<string, unknown>;
    const date = typeof record.date === "string" ? record.date : "";
    const time = typeof record.time === "string" ? record.time : "";
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}$/.test(time)) {
      return { ...EMPTY_PROFILE };
    }
    const [year, month, day] = date.split("-").map(Number);
    const [hour, minute] = time.split(":").map(Number);
    const verified = new Date(Date.UTC(year, month - 1, day));
    if (year < 1900 || year > 2099 || verified.getUTCFullYear() !== year ||
        verified.getUTCMonth() + 1 !== month || verified.getUTCDate() !== day ||
        hour > 23 || minute > 59) {
      return { ...EMPTY_PROFILE };
    }
    return { date, time };
  } catch {
    return { ...EMPTY_PROFILE };
  }
}

export function saveBirthProfile(profile: BirthProfile): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(profile));
  } catch {
    // Browsers may disable local persistence. The calculation still works.
  }
}

export function clearBirthProfile(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // Clearing best-effort local storage does not affect server-side state.
  }
}
