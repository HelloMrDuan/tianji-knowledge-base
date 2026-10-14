import { useCallback, useEffect, useState } from "react";

/**
 * TJ-008.6 双主题基础。
 *
 * - 深青夜景（night）为默认主题，米白宣纸（paper）为可切换主题。
 * - 偏好保存在 localStorage["tianji.theme"]；非法值回退为默认。
 * - index.html 内联脚本在首屏绘制前应用主题，避免闪烁；
 *   这里负责运行时切换与持久化。
 */
export type Theme = "night" | "paper";

export const THEME_KEY = "tianji.theme";
export const DEFAULT_THEME: Theme = "night";

const THEME_COLORS: Record<Theme, string> = {
  night: "#0b1c23",
  paper: "#143d36",
};

export function resolveTheme(raw: string | null | undefined): Theme {
  return raw === "paper" ? "paper" : DEFAULT_THEME;
}

export function readTheme(): Theme {
  try {
    return resolveTheme(window.localStorage.getItem(THEME_KEY));
  } catch {
    return DEFAULT_THEME;
  }
}

export function applyTheme(theme: Theme): void {
  const t = resolveTheme(theme);
  document.documentElement.setAttribute("data-theme", t);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", THEME_COLORS[t]);
  try {
    window.localStorage.setItem(THEME_KEY, t);
  } catch {
    /* 存储不可用时仅本次生效 */
  }
}

export function useTheme(): [Theme, (next: Theme) => void] {
  const [theme, setTheme] = useState<Theme>(() => readTheme());
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);
  const set = useCallback((next: Theme) => setTheme(resolveTheme(next)), []);
  return [theme, set];
}
