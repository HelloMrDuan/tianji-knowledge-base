# TJ-018.1 Source Coverage Audit — blob_sha Registration (2026-11-13)

## Scope

TJ-018.1 (WBS: 寻找具体古籍条目的底本/版本/合法引用) requires, for each
specific classical entry: version, license, fixed commit/byte hash,
page/line/char position — "不能'搜索到一句话即入库'" (a sentence found
by search is not enough to register).

This batch registers the **fixed byte hash** (`blob_sha`, the git blob
SHA of the upstream file at the pinned commit) for every classical
source in `config/knowledge_sources.json` that was missing it.

## Coverage found (firsthand, main 346450a)

- Registry: **103 sources** (schema_version 1.0).
- By kind: classical 97, implementation 6.
- Classical sources missing `blob_sha` before this batch: **75**.
- Of those 75, **74 resolved** to a verified upstream blob SHA.
- The remaining 1 is correctly empty by design (see below).

## What was registered (74 blob_sha values)

| Group | Count | Upstream repo @ pinned commit |
|---|---|---|
| bazi.source.xieji-relations （钦定协纪辨方书） | 1 | garychowcmu/daizhigev20 @ 4a6d6f20 |
| fengshui.source.zhaifa-phase2 （宅法举隅） | 1 | garychowcmu/daizhigev20 @ 4a6d6f20 |
| liuyao.source.bushi （卜筮正宗）, zengshan （增删卜易） | 2 | yaomancy/liuyao-engine @ 53291663 |
| yijing.source.shuogua, xici, xici_xia, xugua, zagua, tuan_xiang_wenyan (ten wings) | 6 | garychowcmu/daizhigev20 @ 4a6d6f20 (all from 周易.txt) |
| yijing.source.zhouyi01–64 (64 hexagrams) | 64 | sunls2/zhouyi @ 695013f277dc (one file per hexagram, docs/NN.<name>/index.md) |

Total: **74 registrations**. The only file changed is
`config/knowledge_sources.json` (74 lines, blob_sha only; no other
field touched). Test: `tests/test_tj0181_source_blob_sha.py`
(5 tests + 74 pinned-value subtests).

## Verification method (blob_sha convention)

`blob_sha` is the git blob hash of the **upstream** file at the pinned
commit — not of the local snapshot/extract. Proof, verified firsthand:

1. The dream source's registered blob_sha `0c7b0823…` equals the
   upstream `周公解梦.txt` blob at commit 4a6d6f20 (GitHub contents
   API), while the local excerpts file (649 bytes) hashes to a
   different blob. So the local file being an extract does not
   invalidate the blob_sha.
2. The already-registered meihua/benyi blob_sha values match the
   daizhigev20 tree exactly (same method).
3. The xieji local snapshot (762673 bytes, sha256 matches the
   registry) is smaller than the upstream file (834869 bytes) because
   it is an extract; the upstream blob SHA `687e83a6…` still
   identifies the source file correctly.
4. All three upstream trees were fetched via the GitHub recursive
   tree API and were **not truncated** (daizhigev20 15912 entries,
   sunls2/zhouyi 897, yaomancy/liuyao-engine 47). Each blob_sha was
   matched by exact (repository, commit, path); every value is a
   valid 40-hex git SHA.

## Not registered, with reason (not gaps in this batch)

- **bazi.source.zipingzhenquan** （子平真詮）: `provenance_kind`
  is `library_scan` (NLC library scan, not a git repo). `commit` and
  `blob_sha` are correctly null by design; `catalog_id`
  (NLC416-11jh010455-35296) + `pdf_sha256` (71402a78…) identify it
  instead (schema E0381). Nothing to fill.
- **6 implementation sources** (kind=implementation: najia,
  qfdk, lunar-python, iztro, fengshui-master, kinliuren): code
  implementations, not classical entries. Their blob_sha is a
  separate concern and is not filled in here.
- **Author fields left empty** (ditiansui-spouse, qiongtong,
  xieji-relations, yuanhai): the registry's own `era`/`review_scope`
  explicitly states authorship/version questions are not adjudicated
  in this round ("成书与版本问题不在本轮裁定"). Filling authors
  from general knowledge would be fabrication; left as-is.
- **千里命稿 / 果老星宗**: listed in the L2 classics summary but
  have zero references in code, sealed canonical, or evidence
  (千里命稿 appears only as 《千里马》, a different book quoted
  inside 三命通会；果老星宗 0 hits). No entry to register.
- **bazi.source.ditiansui / bazi.source.sanming / bazi.source.xieji**
  (bare ids): not referenced in code (only the suffixed forms
  ditiansui-spouse, sanmingtonghui, xieji-relations are used). The
  one `bazi.source.xieji (sources[95])` string resolves to the
  registered xieji-relations entry. No gap.

## Result

After this batch: classical 97, with blob_sha 96, without 1
(zipingzhenquan, library_scan, by design). Every classical source
that can carry a blob_sha now does.
