# TJ-008.7 第四轮精准整改 · 对照报告（2026-10-15）

基准：`docs/product/designs/night-ink/approved-reference.webp`
分支：`tj-008.7-night-home-restoration` → PR #241（待视觉审核，不合并）
美术素材：沿用第三轮 6 张原创 AI 水墨，未重做。

## 五项整改完成情况

### 1. Hero 遮罩 CSS 覆盖（已修复）
- `night-home.css` 曾定义两次 `.night-hero-night::after`，后者覆盖前者，
  中部径向变暗遮罩失效。已合并为唯一规则：径向遮罩（文字可读）+
  底部渐变（向页面底色过渡）同时生效。
- 桌面/390/360 实测：标题、副标题、正文、按钮在绘景上均可读（截图为证，
  非仅纯色对比度门禁）。

### 2. 桌面四卡与夜景融合（已调整）
- `.night-cards-section` 加 `margin-top: -70px`，四卡上叠 Hero 底部，
  如原图庭院一体；背景改为顶部透明渐变，z-index 3。
- 1440px 首屏（1000px 视口）同时可见完整 Hero + 四张主卡（截图为证）。
- 四卡顺序：今日运势 → 桃花姻缘 → 事业财运 → 流年运势；真实 React 路由，
  非静态图片。

### 3. 手机首屏（已优化，实测通过）
- 第五轮修复遮挡根因：手机 Hero 的 4 个 CTA 按钮与下方四张主卡重复，
  在 ≤640px 隐藏 Hero 按钮组（四入口由紧凑列表承载，功能不丢失）；
  卡片区 `margin-top: -70px` 改为双主题通用（纸主题此前为 0）。
- Playwright 严格几何测试（`scrollY===0`，实测矩形 vs 导航顶部 - 4px）：
  - 390×844 夜景：四行 bottom 525/605/685/765，导航 top 784 → 通过
  - 360×800 夜景：四行 bottom 489/567/645/723，导航 top 740 → 通过
  - 390×844 纸主题：通过；360×800 纸主题：通过
- 新增 4 个专用测试（2 主题 × 2 视口），全量 39/39。
- 无横向溢出；标题/音乐/主题按钮/底部导航无遮挡；字号不低于 13px。
- 证据：`viewport-night-390/360.png`、`viewport-paper-390/360.png`
 （未滚动的首屏视口截图）。

### 4. 首页文案精简（已调整）
- Hero 描述改为：「以真实历法推演时序流转，参已审核的传统典籍，
  看今日运势结构，亦观桃花、事业与财运。」删除技术免责长句。
- `scenario-proof` 弱化为 12px / 0.62 透明度，不再是视觉主体。
- 未新增任何吉凶评分、婚期、收入预测；知识边界由结果页与功能本身承载。

### 5. 图片加载（已验证）
- `NightHeroScene.tsx` 改用 `<picture><source media="(max-width: 640px)">`，
  按视口只加载一张；纸主题下不渲染 `<picture>`（MutationObserver 跟踪
  `data-theme`），不请求夜景大图。
- Playwright Network 实测：
  - 桌面 1440：仅 `hero-desktop-*.jpg`（1 张）
  - 手机 390/360：仅 `hero-mobile-*.jpg`（1 张）
  - 纸主题：0 张 hero 图（仅 4 张 lazy 卡片图）
  - 无第三方网络请求。
- `ART_ASSETS.md` 已更正：素材在 `src/assets/night-home/`（vite 打包进
  `dist/assets/`），非 `public/`；加载说明改为 `<picture>` 单图机制。

## 测试（本地真实 Chromium）
- `npm run build`：通过；`check_public_web_bundle.py`：通过
- 对比度 night/paper：双通过；主题 25/25
- `original-design-home` + `whole-site`：35/35
- `test_task_tracking.py`：OK；台账门禁：PASS（94 任务 / one-task PR=TJ-008.7）

## 仍未解决的差异
1. 生成绘景为单体楼阁，原图是更开阔的多灯笼庭院 terrace。
2. 月亮偏大偏亮（风格差异）；卡片为 AI 水墨非手绘。
3. 未做 WebP/AVIF 二次压缩（合计 1.23MB）。
