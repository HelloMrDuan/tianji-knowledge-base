type Name =
  | "arrow"
  | "chevron"
  | "search"
  | "music"
  | "pause"
  | "play"
  | "volume"
  | "close"
  | "menu"
  | "star"
  | "clock"
  | "book"
  | "grid"
  | "layers"
  | "check"
  | "shield"
  | "file"
  | "settings"
  | "external"
  | "filter"
  | "plus"
  | "sun";
const paths: Record<Name, string> = {
  arrow: "M5 12h14m-6-6 6 6-6 6",
  chevron: "m8 5 7 7-7 7",
  search: "M16 16l5 5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0",
  music:
    "M9 18V5l11-2v13M9 18c0 2-5 3-5 0s5-3 5 0m11-2c0 2-5 3-5 0s5-3 5 0M9 8l11-2",
  pause: "M8 5v14m8-14v14",
  play: "m8 5 11 7-11 7Z",
  volume: "M4 9h4l5-4v14l-5-4H4Zm13-7c3 3 3 7 0 10",
  close: "m6 6 12 12M18 6 6 18",
  menu: "M4 6h16M4 12h16M4 18h16",
  star: "m12 3 2.8 5.7 6.3.9-4.5 4.4 1 6.2-5.6-2.9-5.6 2.9 1-6.2L2.9 9.6l6.3-.9Z",
  clock: "M12 6v6l4 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0",
  book: "M3 4h7l2 2 2-2h7v16h-7l-2 1-2-1H3ZM12 6v15",
  grid: "M3 3h7v7H3Zm11 0h7v7h-7ZM3 14h7v7H3Zm11 0h7v7h-7Z",
  layers: "m12 2 10 6-10 6L2 8Zm-10 10 10 6 10-6M2 17l10 6 10-6",
  check: "m5 12 4 4L19 6",
  shield: "m12 2 9 4v7c0 5-9 9-9 9S3 18 3 13V6Z",
  file: "M5 2h9l5 5v15H5Zm9 0v6h5M8 12h8M8 16h6",
  settings:
    "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2",
  external: "M14 3h7v7m0-7L10 14M10 3H3v18h18v-7",
  filter: "M3 5h18l-7 8v6l-4 2v-8Z",
  plus: "M12 4v16M4 12h16",
  sun: "M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
};
export function Icon({
  name,
  size = 20,
  className = "",
}: {
  name: Name;
  size?: number;
  className?: string;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
    >
      <path d={paths[name]} />
    </svg>
  );
}
