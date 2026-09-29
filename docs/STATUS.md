# Current Status

更新时间：2026-09-29

## 已落地

- 正式来源注册：22 个
- GitHub 全网候选池：270 个仓库 / 14 组检索词
- 自动来源发现：每日
- 自动许可证与仓库健康审计：每日
- 已登记来源 commit 检查：每 6 小时
- 审核白名单文件实际刷新：每 6 小时
- 三层策略：RAW / QUARANTINE / CANONICAL
- 明确支持子包独立许可证，例如 taibu/packages/core MIT，不继承根 AGPL

## 周易 / 八卦

- 八卦结构：8
- 六十四卦结构：64
- 完整卦辞：64
- 完整大象：64
- 完整爻辞：384
- 《文言》：乾、坤
- 周易检索索引：473 条
- 现代断语与古典原文分离

## 六爻 / 梅花

- 《卜筮正宗》公版全文：99,634 字符
- 《增删卜易》公版全文：132,885 字符
- 六爻公版原典 RAG：219 块
- 六爻规则索引：38 条
- 梅花规则索引：1 个规则包
- 八纯卦纳甲、六亲、六神基础规则已入库

## 八字 / 姻缘

- MIT 八字规则源已同步：经典摘要、大运、神煞、时辰、五行表
- 八字 RAG 索引：94 条
- 合婚规则索引：9 条
- 无 LICENSE 的姻缘项目保持 REFERENCE_ONLY，不进入商业 Canonical

## 自动化

- validate.yml：Canonical 完整性验证
- kb-sync.yml：来源 commit / license 元数据同步
- refresh-manifest.yml：审核白名单文件刷新
- source-discovery.yml：GitHub 新源发现
- audit-candidates.yml：候选 License / 健康度审计

## 下一批

1. 补《彖传》与《象传》逐爻小象结构。
2. 补《系辞》《说卦》《序卦》《杂卦》公版原典。
3. 将 6tail/lunar-python 接成确定性历法/干支适配层。
4. 接 iztro 的紫微确定性排盘适配层。
5. 清洗奇门、大六壬、太乙的计算规则与固定案例。
6. 对 270 个候选仓库逐批 License 审计，优先晋级宽松许可证高价值源。
7. 设计 PostgreSQL + pgvector 混合检索和 Citation-first API。
