# TJ-008.7 第三轮视觉整改 · 对照报告（2026-10-14）

基准：`docs/product/designs/night-ink/approved-reference.webp`（+ with-music-reference.webp 手机样式）
分支：`tj-008.7-night-home-restoration` → PR #241（待视觉审核，不合并）

## 根本转变

停止用 SVG 几何堆砌模拟水墨。本轮 6 张视觉素材全部为 AI 原创生成
（Muse media.generate_image），经实际打开筛选，无文字乱码、无水印、无人物，
非第三方受保护图片，更非设计参考截图。素材清单见 `ART_ASSETS.md`。

## 实际重做内容

### 1. 桌面 Hero（`NightHeroScene.tsx` 简化为绘景 + HTML 叠加）
- 背景：`hero-desktop.jpg`（2048×1152 原创水墨：楼阁露台/格栅暖窗/大灯笼/
  梅枝/满月/层峦/湖月影/湖岸灯火/薄雾）
- 文字/按钮/印章仍为真实 HTML/React，可交互；叠加可读性渐变
- 不再有任何 SVG 场景代码

### 2. 手机 Hero（独立竖构图）
- 背景：`hero-mobile.jpg`（1152×2048）
- Hero 高度压缩至 460px（原 560px），不霸占首屏

### 3. 手机紧凑列表（按原图手机端）
- 新增 `MobileCardRow`：缩略图 + 标题 + tagline + 右箭头，4 行
- ≤640px 显示列表、隐藏 4 张大卡；桌面反之
- 真实路由不变

### 4. 四张卡（`PaperCard.tsx`）
- 插画改为 `art-*.jpg`（日出/桃花/策马/层峦，`loading="lazy"`）
- 宣纸纹理保留；顺序/路由/文案不变

### 5. 卡片与 Hero 衔接
- 夜景区卡片段加深色渐变过渡，不再是白卡悬浮

## 已消除的差异

- SVG 扁平感 → 真实水墨质感
- 手机宽幅裁切 → 独立竖构图，月/阁/灯/山/水齐全
- 手机四张大卡占屏 → 紧凑列表
- 卡片悬浮割裂 → 渐变自然衔接

## 仍未解决的差异（诚实记录）

1. 生成绘景的楼阁为单体建筑，原图是更开阔的庭院 terrace（含多灯笼、
   案头陈设）；意境相近，细节密度仍不及原图。
2. 生成图月亮偏大偏亮，原图月亮更含蓄；属风格差异。
3. 卡片插画为 AI 水墨，原图为手绘水墨；神似。
4. 未做 WebP/AVIF 二次压缩（JPG quality 88，合计 1.23MB），后续可优化。

## 测试（本地真实 Chromium）
- build：通过；对比度 night/paper：双通过；主题 25/25
- `original-design-home` + `whole-site`：35/35（含新增手机列表断言）
- 台账门禁：PASS（94 任务 / one-task PR=TJ-008.7）
