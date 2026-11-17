/**
 * TJ-029.2 P1: 统一清除本机资料。
 *
 * 天机在浏览器本地只用这 5 个 localStorage 键（Line A 2026-11-16 核查）：
 * 只有出生资料档案含个人身份信息，其余 4 个是偏好。
 * 此前只有出生资料可单独清除，没有一键清除全部的入口，合盘页甚至
 * 没有任何清除按钮。本模块是唯一的清除入口登记处。
 */

export const LOCAL_DATA_KEYS: ReadonlyArray<{ key: string; label: string }> = [
  { key: "tianji.profile.birth.v1", label: "出生资料档案" },
  { key: "tianji.scenario.target-year.v1", label: "目标年份" },
  { key: "tianji.product.favorite", label: "收藏偏好" },
  { key: "tianji.prototype.music", label: "音乐偏好" },
  { key: "tianji.theme", label: "主题偏好" },
];

/** 当前实际保存在本机的资料类别（按登记顺序）。 */
export function presentLocalDataLabels(): string[] {
  const labels: string[] = [];
  for (const { key, label } of LOCAL_DATA_KEYS) {
    try {
      if (localStorage.getItem(key) !== null) labels.push(label);
    } catch {
      // 存储不可用时按“无”处理
    }
  }
  return labels;
}

/**
 * 清除全部 5 个键；返回实际被清除的类别。
 * 只删登记的键，不碰其他站点的存储。best-effort：单个键失败不中断其余。
 */
export function clearAllLocalData(): string[] {
  const cleared: string[] = [];
  for (const { key, label } of LOCAL_DATA_KEYS) {
    try {
      if (localStorage.getItem(key) !== null) {
        localStorage.removeItem(key);
        cleared.push(label);
      }
    } catch {
      // best-effort
    }
  }
  return cleared;
}

/**
 * 跨标签页同步：其他标签页删除任一登记键时触发。
 * storage 事件只在其他文档触发，当前标签页清除时不会自触发。
 * 出生资料键在 5 键之内，因此出生资料清除与全部清除都走同一监听。
 */
export function onLocalDataCleared(callback: () => void): () => void {
  const keys = new Set(LOCAL_DATA_KEYS.map((item) => item.key));
  const handler = (event: StorageEvent) => {
    if (event.key && keys.has(event.key) && event.newValue === null) {
      callback();
    }
  };
  window.addEventListener("storage", handler);
  return () => window.removeEventListener("storage", handler);
}
