# 旺衰第二批：阴阳五行与生克位置

沿用现有 Source、RAW/Quarantine、逐字短引 Review、Phase1 实体、SourceRef、Variant、Golden、Phase2 和 Scenario。没有建立新权重表、另一个知识 schema 或全局旺衰公式。

本批增加 4 条短引、5 个 Terms、1 条可执行位置规则、4 个手工固定 Golden。`ditiansui-root-visibility-v1` 仍为 **PARTIAL 因素观察**；整体强弱分类未完成，不能因此解除格局、喜用或岁运解释的缺失依赖。

| Section | 原典 | 审核范围 |
|---|---|---|
| s030 | 《渊海子平》论五行生剋制化 | 金生水、水生木、木生火、火生土、土生金；保留同段多、盛等效力条件 |
| s031 | 同上 | 金剋木、木剋土、土剋水、水剋火、火剋金；保留坚、重等条件和原字“剋” |
| s032 | 《滴天髓阐微》天干·原注 | 甲丙戊庚壬阳、乙丁己辛癸阴 |
| s033 | 同篇任氏注 | 甲乙木、丙丁火、戊己土、庚辛金、壬癸水 |

只核已有 `bazi.source.yuanhai` 和 `bazi.source.ditiansui-spouse` 的固定原文快照。原典 quote、字符定位、byte SHA、commit 及已有隔离 RAW 候选可追查；不改原始文件，不据完整电子本含原注就采用现代按语，保持 C 级，不冒充独立底本完成。

新增 Term 为天干、阴阳、五行、生克、生扶克泄耗关系；关系观察继续引用既有十神和藏遁歌。对应 Rule r016 / `bazi.phase2.support_relations`，操作使用既有 `foundations` 中的阴阳五行和生克表、`ten_god` 及藏干表，新增审核绑定来验证原表方向，不另算一套排盘。

显式选择因素 Variant 后，八字基础场景返回相对日主的三处显干与全部藏干位置，区分 `same_element / generates_me / i_generate / controls_me / i_control`。日干仅作参照，不额外作为一处自扶。每条 RuleMatch 有原典 Evidence，`bazi.support_relations` 只绑定实际命中的位置事实。

方向不等于效力：同类多不证明身强，生我不必有益，克我不必为凶，透印不证明得势，合冲不自动改变这些方向或判根损。`effective_support / de_shi / overall_strength` 保持 null，不计算数量评分或喜忌。

四个合成结构 Golden 分别验证一般五行方向及完整藏干位置、阴日干生克与阴阳关系、多比肩不判强、冲克不定凶。另有十干完整分类、默认关闭、真实场景 Evidence 绑定和无依据喜用拒绝测试。Golden 的输入是结构测试样本，不宣称来自真实出生记录；期望未由待验证算法生成。

剩余旺衰依赖包括司令分日异文、实际根力、季节和生扶克泄耗效力、得地得势条件及从化/旺极衰极边界。原典直接反对机械得时即旺和数量判断；这些缺口须核文本和流派，不能因产品需要直接填公式。
