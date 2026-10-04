export type ReadingRecord = {
  id: string;
  scenarioId: string;
  label: string;
  glyph: string;
  title: string;
  subtitle: string;
  href: string;
  createdAt: string;
  resultVersion?: string;
  favorite: boolean;
  storage: "browser-local";
};

export type NewReading = Omit<ReadingRecord, "id" | "createdAt" | "favorite" | "storage">;

const storageKey = "tianji.product.readings.v1";
const changeEvent = "tianji:readings-changed";
const maxRecords = 50;

function isRecord(value: unknown): value is ReadingRecord {
  if (!value || typeof value !== "object") return false;
  const item = value as Record<string, unknown>;
  return (
    typeof item.id === "string" &&
    typeof item.scenarioId === "string" &&
    typeof item.label === "string" &&
    typeof item.glyph === "string" &&
    typeof item.title === "string" &&
    typeof item.subtitle === "string" &&
    typeof item.href === "string" &&
    typeof item.createdAt === "string" &&
    typeof item.favorite === "boolean" &&
    item.storage === "browser-local"
  );
}

export function loadReadings(): ReadingRecord[] {
  try {
    const raw = localStorage.getItem(storageKey);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isRecord).slice(0, maxRecords);
  } catch {
    return [];
  }
}

function persistReadings(records: ReadingRecord[]) {
  try {
    localStorage.setItem(storageKey, JSON.stringify(records.slice(0, maxRecords)));
    window.dispatchEvent(new Event(changeEvent));
  } catch {
    /* Browser-local journal is optional; calculation results must remain usable. */
  }
}

function makeId() {
  try {
    return crypto.randomUUID();
  } catch {
    return `reading-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  }
}

export function recordReading(reading: NewReading): ReadingRecord {
  const record: ReadingRecord = {
    ...reading,
    id: makeId(),
    createdAt: new Date().toISOString(),
    favorite: false,
    storage: "browser-local",
  };
  persistReadings([record, ...loadReadings()]);
  return record;
}

export function toggleReadingFavorite(id: string): ReadingRecord[] {
  const next = loadReadings().map((item) =>
    item.id === id ? { ...item, favorite: !item.favorite } : item,
  );
  persistReadings(next);
  return next;
}

export function removeReading(id: string): ReadingRecord[] {
  const next = loadReadings().filter((item) => item.id !== id);
  persistReadings(next);
  return next;
}

export function subscribeReadings(listener: () => void) {
  window.addEventListener(changeEvent, listener);
  window.addEventListener("storage", listener);
  return () => {
    window.removeEventListener(changeEvent, listener);
    window.removeEventListener("storage", listener);
  };
}
