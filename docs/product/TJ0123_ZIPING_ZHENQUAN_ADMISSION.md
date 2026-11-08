# TJ-012.3《子平真詮》来源准入＋第十六章平行登记（E0382）

用户 2026-11-05 裁定（Option 1）准入 1925 上海世界圖書館版《子平真詮》
為獨立來源，授權第十六章《論雜氣如何取用》最小平行登記批；2026-11-06
四項裁定（Schema 修訂先行、TXT 人工轉錄、密封建節納入本批、命名確認）
逐項批复（第 1 項改、第 2–4 項同意）。Schema 修訂已先行合併（E0381，
PR #554，Merge SHA `4640f960ce0ac0c2f7cebf59e6a9e28c4ef4942f`）。
機器可讀登記與本文件同源：`src/tianji_kb/bazi_registration_governance.py`
的 `TJ0123_ZIPING_ZAQI_RECORD` 與 REGISTRATION_INVENTORY 的
`ziping-zaqi-ch16` 項、新模塊 `src/tianji_kb/bazi_ziping_zaqi.py`
（公開專項 `tests/test_tj0123_ziping_zaqi_public.py` 釘住三者一致性；
密封專項 `tests/test_tj0123_ziping_zaqi_sealed.py` 只在離線驗收運行）。

**先行結論（與准入授權一致）**：本批完成了來源登記與 Ch16 平行登記，
但**准入 ≠ 裁定**——Ch16 教義不可執行（§3），`evidence_binding`
維持 `pending`、Phase1 規則與 Phase2 步皆無、determination 恒 None。
本批不宣稱雜氣定格、真假、成敗、用神或吉凶解鎖；Slice B、三命卷五
與 Ch16 三說并列、不裁定；TJ-012.3 保持阻塞。

## 1. 底本身份與來源登記

- 底本：1925 上海世界圖書館版《子平真詮》，館藏
  `NLC416-11jh010455-35296`，PDF SHA256
  `71402a780b0351b54edf121a51bc4a4a4ce5896496c35b954563ee06f1a6f620`，
  7,126,096 字節、287 頁（純圖像掃描，無文本層）。文件頁 URL 見來源
  記錄 `review_scope`；直鏈上傳前已驗 200。
- 作者：沈孝瞻；作者歸屬有爭議（傳統題沈孝瞻 vs《耕寸集》說），
  1925 版不作沈氏手稿或早期版本逐字副本之稱；1895／1923 版未確認，
  本批不援引。
- 來源記錄 `bazi.source.zipingzhenquan`（`config/knowledge_sources.json`
  第 103 條）：`provenance_kind=library_scan`、`commit=null`（無 Git
  commit 存在，不編造）、`catalog_id=NLC416-11jh010455-35296`、
  `pdf_sha256=71402a78…f620`、`content_path=
  data/quarantine/public_domain_snapshots/nlc416/
  zipingzhenquan_1925_ch16.txt`、`sha256=
  98576342cd8c4fb092a7bec5c1e86b7b02c051cb14a9c6a7f632f5a42b647966`、
  `blob_sha=null`（密封樹非 git 倉庫，無可驗證 Git blob）、C 級、
  `kind=classical`。`config/phase2_source_audit.json` 同步增譜系行
  （lineage_group `NLC416-11jh010455-35296`，無 GitHub 譜系、不與
  任何 GitHub 來源同組、不投獨立票，edition／authority 均 unverified、
  grade_ceiling C）。
- 來源普查：登記表 102 → 103 條，C:96 → C:97、D:6 不變。
- TXT：僅 Ch16 正文三頁（掃描 41–43，原書 32–34），人工逐字轉錄、
  300-dpi 渲染逐字核對；2,464 字節，821 字正文＋結尾 LF，UTF-8 無
  BOM、LF、零 PUA。章界已核：掃描 42 末字「似」跨頁接掃描 43 首句，
  Ch16 止於掃描 43「傍悟而已。」；第十七章篇名僅見於掃描 43 左邊欄，
  正文始於掃描 44——本批不含第十七章任何正文。附錄（偉人星命錄、
  萬年書）與徐樂吾評注（美國保護至 2032-01-01）排除在外；本版此三頁
  全為大字正文、無小字注，無注釋層可排除。

## 2. Canonical 建節（密封側著錄）

私有數據樹（可信機受控檢出的暫存副本）`data/canonical/bazi/
phase1_knowledge.json` 純增量變更，實體計數：classics 6→7、chapters
44→45、sections 184→185，terms 39、rules 51、concepts 18 不變：

- 新增 classic `bazi.classic.zipingzhenquan`（子平真诠，
  `source_id=bazi.source.zipingzhenquan`，`body_stage=quarantine`）。
- 新增 chapter `bazi.chapter.ziping_zaqi`（論雜氣如何取用）。
- 新增 section `bazi.section.s185`（雜氣如何取用，子平真詮第十六章
  全文）：文本為密封 TXT 正文 [0,821) 逐字（821 字），`review.status`
  為 `approved`（形制沿 s065／s066／s067／s024），`review.scope`
  明載 evidence_binding 維持 pending、只建節不建規則不建步、疑字
  機制句／理由句不可引。
- 密封變更文件恰 3 個：TXT、轉錄工作單
  （`data/quarantine/public_domain_snapshots/nlc416/
  zipingzhenquan_1925_ch16_worksheet.md`）、`phase1_knowledge.json`。
  覆蓋工件 `data/coverage/phase1.json` 已於修復批以密封樹內 `scripts/build_phase1_coverage.py` 重新生成（7 項八字值已更新：chapters 44→45、classics.quarantine 4→5、classics.with_reviewed_excerpts 6→7、production_chunks 292→293、sections 184→185、source_ids 8→9、sources.C 8→9），離線驗收已核驗再生工件。

## 3. 引文綁定驗證（20 條）

20 條引文（B-16-01–B-16-20）逐條復核：於密封 TXT 實測字符偏移逐字
復現，且全數包含於 s185 節文本（機上實測 20／20，每條在 TXT 中恰
出現一次、零 PUA）。核取短引為每條的判讀錨點（每條一核，≤14 字），
彼此不連續（最小闕文 4 字）；公開側覆蓋約三成，餘皆闕文，不可拼出
全章（見 §6 防泄漏回歸）。跨頁「似」（索引 555）僅存密封，不在任何
公開短引內。

### B-16-19 印本訂正（兩字，證據表誤寫）

2026-11-06 引文覆核（300-dpi 渲染＋500-dpi 放大＋全欄重讀）：證據表 B-16-19 引文誤增兩字：開頭「又」後多一「如」字、「並透」後多一句讀圈；印本無此二字。對照：B-16-09 開頭確以「又如」起句；B-16-09／B-16-10／B-16-13 同型句尾在印本中皆有句讀圈——印本此處前後不一致，照錄不一併改動。TXT、locator（B-16-19 核取 [734,738)「透戊為食」）與本模塊引文一律從印本；證據表該條引文的兩字誤寫在此落賬。

先前 Phase 2 轉錄的另兩處糾正亦已核實：掃描 42 頁末恢復「似」（跨頁句「而火能生土。似又清辰中之戊。印格不清。」），B-16-17作「而不貴者也」非「當而不貴者也」。

### 異文（7 項，原樣＋疑讀＋證據分記）

V-01 會何全局（B-16-10，會支成立句存疑，機制不可引）、V-02 似又清
辰中之戊（B-16-16，機制句存疑，不可引；僅 verdict 與救應條件可讀）、
V-03 譬如月規用官（B-16-18，理由句存疑，不可引；verdict 可讀）、
V-04 在即此為例（B-16-20，僅結語措辭）、V-05 竝（照錄）、V-06
朋沖／下成（照錄）、V-07 月劫（照錄，不歸併為劫財）。任何疑字均不
按推測更正；不可引的三條（B-16-10 會支句、B-16-16 機制句、B-16-18
理由句）只禁機制／理由層引用，其 verdict 本身可讀。

### 衝突圖（登記、不裁定）

- 與 Slice B 一般臂直接對立 11 條：B-16-03–B-16-10、B-16-12–B-16-14
  （總綱、透干三例、會支定義、兼用、有情定義及三例、無情三例）。
- 事實層一致 2 條：B-16-01（雜氣定義）、B-16-02（辰藏乙戊癸）。
- B-16-17 為第三立場：與三命卷五喜透露沖刑方向相反（有界：Ch16 例
  專指壬透印格，三命喜沖刑為雜氣格通論），與 Slice B 無沖規則對照。
- 其餘 6 條（B-16-11、B-16-15、B-16-16、B-16-18、B-16-19、B-16-20）
  無登記對照（新分級／二階翻轉／作者自限），不構成對立。
- 章外張力僅備錄：Ch 8「是建祿月劫之格。非用而即用神也。」與 Slice A
  祿刃路線方向不同；Ch 8 不在本批範圍內，不裁定、不改 Slice A。
- 方向 A（TJ-011.2）零增量：全章日主僅甲、丙、壬、癸，無戊／己日主例；
  土根分級、有效根標準、日主強弱形態皆無新句。

## 4. 執行鏈核查（決定不翻轉的核心實證）

1. Ch16 教義無可執行謂詞：清（B-16-03 等）無定義、無閾值、無檢驗法，
   且既是選用標準又是結論；有情／無情（B-16-07、B-16-11）為未定義
   謂詞，無事實類型、無閾值、無判定程序；會支（B-16-05 等）未定義
   何種支組算數，僅三局有例、無通用三合規則；兼用次序、去暗土、
   作合／壞印、土動／月令、所剋者轉向皆無可執行事實類型。
2. 新模塊 `bazi_ziping_zaqi.py` 為純數據登記：三個查表函數（按 id 取
   引文／對照／登記姿態，fail-closed），不接 `operations/bazi_chart`，
   不經 ExecutionTrace、無 RuleMatch 產出；Phase2 golden harness 只
   執行 `operations.*` provider，本切片無從 fire。
3. S5 翻轉先例的標準是 Phase1 規則＋Phase2 規則＋見證盤經註冊規則步
   發出三者齊備；只建 Phase1 聲明規則而無執行步，按治理登記冊自身
   定義即 `execution_binding_structure` 的「無執行步的空註冊」
   （ren-pattern-yin-true-v1 同類處置）。
4. 作者自限（B-16-20）：章內自認例證不可窮舉、只供類推；不得把
   B-16-01–B-16-19 抽為封閉可執行規則集。

結論：註冊前提不成立，`evidence_binding` 維持 `pending`。缺口登記
為治理項 `ziping-zaqi-ch16`（disposition maintained_pending、
reason_class `execution_binding_structure`）；Canonical 建節已消除
本切片原有的 canonical_evidence_absent 面，剩餘缺口只有執行綁定
結構一項。解鎖路徑＝用戶裁定某條教義可執行化並審定其閾值／判定程序、
且接入 ExecutionTrace 後，再行註冊。本批未觸碰該步，未偽造任何
執行綁定。

## 5. manifest 釘值記錄（不靜默改釘）

- 暫存快照：237 → 239 文件（新增 TXT 與轉錄工作單兩件），總字節
  16,722,816 → 16,739,253。
- manifest SHA256：`26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`
  → `eca717ef4b8bf8e08de00e2b24ac4ecddfa2dbe815a141b7e19d63668699d2ff`。
- 釘值狀態：新釘值即 `eca717ef…`；live 快照換位、
  `cicd/env/trusted-acceptance` 改釘與私有構建腳本釘值更新**須與本 PR
  合併同步執行**（父級），本批未先行替換任何一端（live 快照仍為
  `26b63e64…`、pin 未動），暫存快照只用於機上復跑。回退路徑不變
  （恢復舊快照目錄＋舊釘值）。
- 逐文件 SHA256：TXT 已釘 `98576342…f647966`（見 §1）；其餘兩文件
  （工作單、`phase1_knowledge.json`）的逐文件 SHA256 以機上暫存快照
  manifest（`eca717ef…`）為準，由離線驗收復核；公開側不推算、不補寫。

## 6. 驗證

- 公共檢查（test_tj0123_ziping_zaqi_public.py）涵蓋：核取短引＝Golden 逐字相等且 locator 跨度＝引文長度（每條 ≤14 字）；異文未被默改（含 B-16-19 印本形式——公開側只驗誤寫形式不在、正確短引在，不引全句）；防泄漏回歸（核取短引彼此不連續、公開覆蓋上限、跨核邊界探針與第十七章正文開頭探針不在模塊／Golden／治理文檔）；無執行綁定。密封側另有防泄漏驗收（test_tj0123_ziping_zaqi_sealed.py）：掃描組裝內的公共文件、對密封 TXT 實測最大連續引用與覆蓋率，斷言不可拼出全章。
- 密封專項 `tests/test_tj0123_ziping_zaqi_sealed.py`（只在離線驗收運行）：
  s185 文本與 TXT 正文逐字等值、20 條引文逐片複核且各恰出現一次、
  實體計數（classics 7、chapters 45、sections 185、terms 39、rules 51、
  concepts 18）、`validate_knowledge` 全量通過、無 Ch16 Phase1／Phase2
  規則存在。
- 回歸：既有 pattern／strength／tiaohou／bingyao／dayun 公開模塊零改動
  實測（相關測試全過，見 PR 記錄）；普查釘值隨真實登記增項移動
  （102→103、C:96→C:97），合化審定 `phase1_sections_total` 184→185
  （s185 文本與節名已實測不含合化關鍵詞與「五合」，其餘合化釘值不動），
  不放寬任何判定斷言。
- 覆蓋工件：`data/coverage/phase1.json` 已於修復批以密封樹內 `scripts/build_phase1_coverage.py` 重新生成（見 §2），離線驗收已核驗再生工件；`data/product/knowledge_coverage.json` 與 `data/product/knowledge_dependencies.json` 本次未再生成——離線驗收全量通過（含讀取 knowledge_coverage.json 的 `tests/test_product_coverage.py`），故本批無需再生成；若未來某批判定必需，須由機上工具再生成並重出暫存快照 manifest，不得靜默沿用舊釘值。

## 7. 未覆蓋

- 第十七章《論墓庫刑沖之說》、附錄、評注、其餘 46 章：均不在本批範圍，
  不登記、不推論。
- Ch 8 與 Slice A 的章外張力：僅備錄，未裁定。
- 執行綁定設計批未立項：教義可執行化審定（含閾值／判定程序）與接入
  ExecutionTrace 的 placement 審定屬獨立審定，不在本批授權內。
- 扶抑 U1／U3、長生裁定、司令擴月、TJ-013.2 衝突裁決、TJ-017.2 跨規則
  調用：均不在本批範圍，本批未動。

## 8. 正式驗收與部署記錄（待填：本批止於 PR，不自合併、不部署）

- 合併：待審 PR（本批止於 PR 待合併與正式驗收）。
- 快照換代：待合併時與父級同步執行（見 §5）；換代前 live 快照與
  cicd 釘維持 `26b63e64…`。
- 正式驗收：待合併後由部署管線對合併 SHA 產出（機上全配方復跑，
  含密封專項）；本行保持阻塞，TJ-012.3 不關賬。
- 終局結論不變：evidence_binding 維持 pending，Phase1／Phase2 規則
  皆無；整部《子平真詮》未標記 canonical_ready（單節建節而已）；
  本節建節不解鎖雜氣定格、真假、成敗、用神或吉凶。
