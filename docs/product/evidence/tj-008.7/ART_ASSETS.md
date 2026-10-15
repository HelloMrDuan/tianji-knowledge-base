# TJ-008.7 第三轮 · 美术素材清单（第四轮修订）

生成时间：2026-10-14
生成方式：Muse media.generate_image（AI 原创生成）
使用权：为本项目任务生成的原创素材，无第三方版权，可用于天机命理平台公开仓库。
**非设计参考截图**：未截取、未复制 `approved-reference.webp` 或任何第三方图片。

## 文件位置（真实）

`web/visual-prototype/src/assets/night-home/`，经 vite 打包进入 `dist/assets/`（带 hash）。
**不在 `public/`**：CI 的 public bundle 门禁（fail-closed，仅允许 `dist/assets/` 与
`dist/music/`）禁止 `dist/images/`，故素材以源码 import 方式引入。

## 文件清单

| 文件 | 尺寸 | 大小 | 用途 |
|---|---|---|---|
| `hero-desktop.jpg` | 2048×1152 | 504 KB | 桌面 Hero 背景 |
| `hero-mobile.jpg` | 1152×2048 | 490 KB | 手机 Hero 背景 |
| `art-sunrise.jpg` | 380×480 | 49 KB | 今日运势卡 |
| `art-peach.jpg` | 380×480 | 54 KB | 桃花姻缘卡 |
| `art-horse.jpg` | 490×510 | 72 KB | 事业财运卡 |
| `art-mountains.jpg` | 490×510 | 58 KB | 流年运势卡 |

合计约 1.23 MB。

## 加载方式（第四轮：`<picture>` 单图）

- Hero：`<picture><source media="(max-width: 640px)" srcset="mobile">` +
  `<img src="desktop" fetchpriority="high">`。浏览器按媒体查询只请求一张；
  已用 Playwright Network 监听验证（见 `VISUAL_DIFF_ROUND4.md`）。
- 卡片图：`loading="lazy"`，进入视口才加载；手机缩略图复用同一文件（缓存）。
- 纸主题下 Hero 区不渲染 `<picture>`（CSS 切换显示浅色水墨），不请求夜景大图。
- 均为同源 `dist/assets/` 静态资源，无第三方网络请求。
