# TJ-007.1 后端阻塞证据（2026-10-15）

## 结论
**本地无法启动真实后端进行端到端验证。** 原因：缺少私有知识库，无法构建生产运行时。

## 复现路径

### 1. 场景引擎可用，但执行需要生产运行时
```bash
$ python3 -c "from tianji_kb.scenario_engine import registry; ..."
bazi-profile - production
daily - production_limited
weekly - production_limited
monthly - production_limited
yearly - production_limited
```

### 2. 执行场景时报错
```bash
$ python3 -c "from tianji_kb.scenario_engine import execute_scenario; execute_scenario('bazi-profile', {'value': '2000-01-07T12:00:00+08:00'})"
tianji_kb.runtime_catalog.RuntimeUnavailable: Build the reviewed production runtime before serving requests
```

### 3. 构建生产运行时失败
```bash
$ python3 scripts/build_production_runtime.py
ValueError: Completed domain bundle missing: yijing
```

### 4. 根本原因
- `build/production_runtime.json` 不存在
- 构建需要 `EvidenceResolver(root, review_sources=True)` 读取私有知识库
- 私有库 `HelloMrDuan/tianji-private-knowledge` 存在但无法通过 HTTPS 克隆（无凭据）
- 本地 `data/` 目录完全不存在

## 可验证的部分（不依赖知识库）
- `tianji_kb.calendar.calendar('2000-01-07T12:00:00+08:00')` 正常工作
  - 年柱：己卯，月柱：丁丑，日柱：甲子，时柱：庚午
- 前端请求构造正确（经 Playwright 拦截验证）

## 影响
TJ-007.1 的"真实后端联调"验收项无法完成。前端已就绪（请求构造、结果展示结构、错误处理），
但端到端真实计算验证需等待：
1. 私有知识库可用，或
2. 远程后端服务地址

## 诚实声明
- 前端 5 场景的请求参数构造已验证正确
- 后端真实计算响应未验证（无可用后端）
- 不得将前端流程测试宣传为"后端真实计算通过"
