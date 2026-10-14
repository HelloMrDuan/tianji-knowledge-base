import type { Theme } from "./theme";

interface Props {
  theme: Theme;
  onChange: (next: Theme) => void;
}

/** TJ-008.6 桌面/手机通用主题切换按钮（深青夜景 ⇄ 米白宣纸）。 */
export function ThemeToggle({ theme, onChange }: Props) {
  const next: Theme = theme === "night" ? "paper" : "night";
  return (
    <button
      type="button"
      className="theme-toggle"
      aria-label={theme === "night" ? "切换为米白宣纸主题" : "切换为深青夜景主题"}
      aria-pressed={theme === "night"}
      title={theme === "night" ? "当前：深青夜景，点击切换米白宣纸" : "当前：米白宣纸，点击切换深青夜景"}
      onClick={() => onChange(next)}
    >
      <span className="theme-toggle-glyph" aria-hidden="true">
        {theme === "night" ? "◐" : "◑"}
      </span>
      <span className="theme-toggle-label">{theme === "night" ? "夜景" : "宣纸"}</span>
    </button>
  );
}
