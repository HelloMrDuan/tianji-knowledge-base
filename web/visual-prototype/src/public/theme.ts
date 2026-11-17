import { useCallback, useEffect, useRef, useState } from "react";

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

export function applyThemeDom(theme: Theme): void {
  const t = resolveTheme(theme);
  document.documentElement.setAttribute("data-theme", t);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", THEME_COLORS[t]);
}

export function applyTheme(theme: Theme): void {
  applyThemeDom(theme);
  try {
    window.localStorage.setItem(THEME_KEY, resolveTheme(theme));
  } catch {
    /* 存储不可用时仅本次生效 */
  }
}

/**
 * TJ-029.2: 全部清除后把可见主题恢复为默认，但不写回存储。
 * 若用 useTheme 的 setTheme 重置，挂载/变更 effect 会立即把默认主题
 * 重新写入 localStorage，使“已清除”变回“存在默认值”。此处只改 DOM，
 * 下一次用户显式切换或重载时再由正常流程重新持久化。
 */
export function resetThemeDomToDefault(): void {
  document.documentElement.setAttribute("data-theme", DEFAULT_THEME);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", THEME_COLORS[DEFAULT_THEME]);
}

export function useTheme(): [Theme, (next: Theme) => void, () => void] {
  const [theme, setTheme] = useState<Theme>(() => readTheme());
  // 全部清除时跳过一次持久化：若用 setTheme 回默认，effect 会立即把
  // 默认主题重新写入 localStorage，使“已清除”变回“存在默认值”。
  // 只在主题确实会变化时置位（否则 setTheme 原值返回、effect 不执行，
  // 标志会泄漏到下一次真实切换）。
  const suppressPersistRef = useRef(false);
  useEffect(() => {
    if (suppressPersistRef.current) {
      suppressPersistRef.current = false;
      applyThemeDom(theme);
    } else {
      applyTheme(theme);
    }
  }, [theme]);
  const set = useCallback((next: Theme) => setTheme(resolveTheme(next)), []);
  const resetSilently = useCallback(() => {
    if (theme !== DEFAULT_THEME) {
      suppressPersistRef.current = true;
      setTheme(DEFAULT_THEME);
    }
  }, [theme]);
  return [theme, set, resetSilently];
}
