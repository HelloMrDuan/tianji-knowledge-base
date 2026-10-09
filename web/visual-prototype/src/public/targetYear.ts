/** A shared, bounded year for the four live consumer scenario pages.
 * This preference is browser-local; the calculation is always served by the
 * actual deterministic Scenario Engine, never calculated in the browser.
 */
const KEY = "tianji.scenario.target-year.v1";
export const MIN_TARGET_YEAR = 1901;
export const MAX_TARGET_YEAR = 2098;
// The default follows the visitor's current calendar year; explicit selection
// remains stored only after successful real calculation.
export const DEFAULT_TARGET_YEAR = Math.max(MIN_TARGET_YEAR, Math.min(MAX_TARGET_YEAR, new Date().getFullYear()));

export function isValidTargetYear(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) &&
    value >= MIN_TARGET_YEAR && value <= MAX_TARGET_YEAR;
}

export function readSavedTargetYear(): number {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw || !/^\d{4}$/.test(raw)) return DEFAULT_TARGET_YEAR;
    const year = Number(raw);
    return isValidTargetYear(year) ? year : DEFAULT_TARGET_YEAR;
  } catch {
    return DEFAULT_TARGET_YEAR;
  }
}

export function saveTargetYear(year: number): void {
  if (!isValidTargetYear(year)) throw new Error("请选择 1901 至 2098 的公历年份");
  try {
    localStorage.setItem(KEY, String(year));
  } catch {
    // Browsers with storage disabled can still use the selected year.
  }
}
