# 天机 Phase 5 · 第一轮视觉原型

只评审前台首页、六爻结果、独立后台及三个资产管理示例。数据是明确标注的手工展示资料，没有 API 客户端、拦截服务或模拟模型。不得将此包作为真实排盘或后台资产发布。

```bash
cd web/visual-prototype
npm ci
npm run dev
```

环境：Node.js 24、npm；构建使用固定版本的 React、TypeScript、Vite。音乐和山水 SVG 都为本项目原创，字体使用系统已有字体，没有第三方资源请求。

托管云环境若用户目录不可写，安装时使用 `npm ci --cache /workspace/.onboarding/npm-cache`，不改动系统目录或降低包校验。

```bash
npm run build
npx playwright install chromium
npm test
```

已有系统 Chromium 的云环境可直接执行：

```bash
PROTOTYPE_CHROMIUM=/usr/bin/chromium npm test
```

重现截图先启动开发服务，再执行截图脚本；长截图保留原生固定导航，因此导航的位置对应截取时的屏幕底部。

```bash
npm run dev -- --host 127.0.0.1 --port 4174 --strictPort
# 在另一个终端执行
npm run screenshots
# 有系统 Chromium 时
PROTOTYPE_CHROMIUM=/usr/bin/chromium npm run screenshots
```

截图保存在 `docs/phase5/visual-prototype/screenshots/`，由真实浏览器直接捕获。桌面为 1440 × 1000 视口长截图；手机为 390 × 844 视口截图，另保留 `-mobile-full.png` 完整内容。

原声音频可通过 `python scripts/generate_music.py` 重现（需 ffmpeg）。这是自编五声音阶合成拨弦循环，不使用录音、样本或第三方音乐。

页面路由、组件结构、交互与前后台边界见 [设计验收说明](../../docs/phase5/VISUAL_PROTOTYPE.md)。**视觉确认后，另开任务联调真实 `/api/v1/execute`；不将静态资料包装成正式服务。**
