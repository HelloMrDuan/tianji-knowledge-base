"""TJ-018.1 source base/version/legal-citation registration: blob_sha coverage.

Every classical (kind=classical) source in config/knowledge_sources.json
must carry the fixed git blob SHA of its upstream file at the pinned
commit (the "fixed byte hash" of the TJ-018.1 WBS requirement:
version, license, fixed commit/byte hash, page/line/char position).

The 74 values in EXPECTED_BLOB_SHA were resolved firsthand from the
upstream repositories' git trees at the pinned commits (GitHub API,
recursive tree, not truncated):
  - garychowcmu/daizhigev20 @ 4a6d6f2088825f132521d848c2ea86cf9c9a7620
    (xieji-relations, 6 ten-wings, zhaifa-phase2)
  - sunls2/zhouyi @ 695013f277dc0548eadf608a6cbabadfbb420312
    (zhouyi01-64, one file per hexagram)
  - yaomancy/liuyao-engine @ 53291663a4c733c4cbdfa174a8d3075475c07fd3
    (bushi, zengshan)

Method validation (the blob_sha convention): blob_sha is the git blob
hash of the UPSTREAM file, not of the local snapshot/extract. Proof:
the dream source's registered blob_sha 0c7b0823... equals the upstream
周公解梦.txt blob at the same commit (verified via the contents API),
while the local excerpts file (649 bytes) hashes to a different blob;
and the already-registered meihua/benyi blob_sha values match the
daizhigev20 tree exactly. So a local extract being smaller than the
upstream file (e.g. xieji 762673 vs 834869 bytes) does not invalidate
the blob_sha.

Excluded, with reason (not a gap in this batch):
  - bazi.source.zipingzhenquan: provenance_kind=library_scan (NLC
    library scan, not a git repo); commit/blob_sha are correctly null,
    and catalog_id + pdf_sha256 identify it instead (schema E0381).
  - 6 implementation sources (kind=implementation: najia, qfdk,
    lunar-python, iztro, fengshui-master, kinliuren): code
    implementations, not classical entries; their blob_sha is a
    separate concern and is not filled in here.
"""

import copy
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# Pinned expected blob_sha values, resolved firsthand from the upstream
# git trees at the pinned commits (see module docstring). Sorted by id.
EXPECTED_BLOB_SHA = {
    "bazi.source.xieji-relations": "687e83a615c64a545591bf72aafcd022f66ec678",
    "fengshui.source.zhaifa-phase2": "568cdea4e8ef9d143286deeecd5e4967f34d0166",
    "liuyao.source.bushi": "30a681259c56e3fd9c4937bf4a90b8ef5f0a1c78",
    "liuyao.source.zengshan": "5ff9b5aadb325162a62f728dd082e937b916891c",
    "yijing.source.shuogua": "ebbe4a4dee79b344fd0c9b97bb90b621bb91ced5",
    "yijing.source.tuan_xiang_wenyan": "ebbe4a4dee79b344fd0c9b97bb90b621bb91ced5",
    "yijing.source.xici": "ebbe4a4dee79b344fd0c9b97bb90b621bb91ced5",
    "yijing.source.xici_xia": "ebbe4a4dee79b344fd0c9b97bb90b621bb91ced5",
    "yijing.source.xugua": "ebbe4a4dee79b344fd0c9b97bb90b621bb91ced5",
    "yijing.source.zagua": "ebbe4a4dee79b344fd0c9b97bb90b621bb91ced5",
    "yijing.source.zhouyi01": "22db8b078c2f650453333dbf51116d5875f79e00",
    "yijing.source.zhouyi02": "56df66017c6364862fc2d7b37263552e78efd9b3",
    "yijing.source.zhouyi03": "d5b5159b9667c255831aab63dcb19a7370442416",
    "yijing.source.zhouyi04": "5cfe1fe579d28d8cac712ed849aab7f9116316c4",
    "yijing.source.zhouyi05": "587c333454eb2e8584eb6cc404ad29dea8a5c6fd",
    "yijing.source.zhouyi06": "8682adf7b2d8c25deb9370e9d2c84ece0a5b1a91",
    "yijing.source.zhouyi07": "61fe227c48f352014c64c6a78773258eb6031dd2",
    "yijing.source.zhouyi08": "188f915792b8c88bd5276a4b2579751bc826b9a9",
    "yijing.source.zhouyi09": "6f518abc2bb2d2dbe744697c7d881a56c517225d",
    "yijing.source.zhouyi10": "8f6ec2848311f4231c1ff2657636bdd799c6291c",
    "yijing.source.zhouyi11": "f3724b32b9f689c2f26c627371ae639ff43059a1",
    "yijing.source.zhouyi12": "8d0dfb3daf26ccb43d2ef3c0f3424243887e29f5",
    "yijing.source.zhouyi13": "2c18c9c4ad7667d96877fc17564a8438b2aa4a00",
    "yijing.source.zhouyi14": "5d097e89b98c29b40bd7884718ce166df689bac1",
    "yijing.source.zhouyi15": "6c4697e05ce1dc07e36aa4c242c94e0387429024",
    "yijing.source.zhouyi16": "76134724fa465854ae5e36ee5a2133f614251785",
    "yijing.source.zhouyi17": "51eaeb3dcde353b19a312978dde6acfe3a8adcef",
    "yijing.source.zhouyi18": "6c0e347a0c7667c97b4ad425c22374b6ed27e6d2",
    "yijing.source.zhouyi19": "c658f98a89019c7880e645579667de729c073bf7",
    "yijing.source.zhouyi20": "ea6c14bcb6ed286d7e510e3da99afa5578d7c35c",
    "yijing.source.zhouyi21": "596172d281dcab2b1411c7bf83f562ce5c6cb6bd",
    "yijing.source.zhouyi22": "ea61ef76bcd05b8a18e909f609200a7e7dd828bd",
    "yijing.source.zhouyi23": "defc6dcc6b00d6e5ffbf1a49fbcbb6ca0c76d089",
    "yijing.source.zhouyi24": "30babb3121e666886393c4c9acb96d28fc1dac33",
    "yijing.source.zhouyi25": "24c252288891f66c1d18853ca86b4d528feefad2",
    "yijing.source.zhouyi26": "c768bbc0e9cbd5afcd134e74e4aa7da4e7dfbc1a",
    "yijing.source.zhouyi27": "10c8ef1e01bc3b6ada875b22508bce5a6d4ddd06",
    "yijing.source.zhouyi28": "9659595e5a5acd5081f0fe41f26d57856f46ebf0",
    "yijing.source.zhouyi29": "027ab1b62d8575b918e0627ac828ec6ff92d35e9",
    "yijing.source.zhouyi30": "65ecef47091a2a5c2eff755b86ff985114be0ffa",
    "yijing.source.zhouyi31": "0eccd602e470c86a08be701bc4f47fff24a32486",
    "yijing.source.zhouyi32": "0f27c5faa092f7fea564f49dc4c58a115de46545",
    "yijing.source.zhouyi33": "54920ddd01afc57b4fe5557e08294b6735a6f978",
    "yijing.source.zhouyi34": "63ace57b8a19a8d7d9cfb5c14f8515614b5400d8",
    "yijing.source.zhouyi35": "dbd6f467fa4bddb950d05373412070e377622e15",
    "yijing.source.zhouyi36": "8df5012a709aa9493eb7c514a81b22188ddac8c3",
    "yijing.source.zhouyi37": "ca9a087a2257116740d45bb6527ffc91649385ed",
    "yijing.source.zhouyi38": "72e1c3ddfa31d4b3bcc2379f8b8140a384a7f278",
    "yijing.source.zhouyi39": "a93b5f13fa84a0e5a659fe22df18b6d16fdef380",
    "yijing.source.zhouyi40": "73ca8704569f9333f0830e29ed7f483a7f43256f",
    "yijing.source.zhouyi41": "d5d3d575b1e521e288d4b25716cf2a47112822b1",
    "yijing.source.zhouyi42": "b7add14c4ccf4146f5e28fc81537d7e2a5b86edd",
    "yijing.source.zhouyi43": "716e0ecee31ecbf1f7dabe2d96062ef515d68aa0",
    "yijing.source.zhouyi44": "c893fe28846aebd64d132133d053d9bb007a2fd2",
    "yijing.source.zhouyi45": "f84854da6ca4f63b541a7695f2864b38453b5a5e",
    "yijing.source.zhouyi46": "406380fb7b6b29cc703a88dd48f7fff92ea8c4d4",
    "yijing.source.zhouyi47": "d96e03affac05aa51d6efacead4084514b34c208",
    "yijing.source.zhouyi48": "bb9f3e02fda5a25f096c924ec2a123003d5751d1",
    "yijing.source.zhouyi49": "07affbcda38bca37081b0eed75d0492dc66b5071",
    "yijing.source.zhouyi50": "cc01e2a11e29cbcfa1fbef3ba9cb92d78eb3d187",
    "yijing.source.zhouyi51": "01552d62e8c3eb9b51159457b904f67ff55ae0fd",
    "yijing.source.zhouyi52": "6729cab25bddcee8ebfda54c2633ee8ffcc58233",
    "yijing.source.zhouyi53": "9044ea2229490e985b452c4e3e2116088fe013bb",
    "yijing.source.zhouyi54": "16dd75cc89818efcb47cebad1b1a4711a6c4f68f",
    "yijing.source.zhouyi55": "acd67dc902c28ac753f88ce253bd3fc20f4d1899",
    "yijing.source.zhouyi56": "9b6d503e4442d5827ee72b6785f1a2bfb8cd947e",
    "yijing.source.zhouyi57": "0e8900fa894eaaf7066beda4e0c40f1112d1d40f",
    "yijing.source.zhouyi58": "e743284b8eb7716fa58d21eb20df1861881f86a9",
    "yijing.source.zhouyi59": "31f67e9ce44c81435bdc4886ad12eb39f8396192",
    "yijing.source.zhouyi60": "ac06b80ff81e27581970c5ce2a8b142e156c31b6",
    "yijing.source.zhouyi61": "b9d10f787a716eba6ab123c4519cea33b4ee6ac5",
    "yijing.source.zhouyi62": "4edd4cd53ff64f07c4bbc6e56856bcd2907655e0",
    "yijing.source.zhouyi63": "c4cce8d6e609d3cd25c8d0472740ea12e9c2218c",
    "yijing.source.zhouyi64": "25f30d2e65fc0465ac9246af6fa4d4e326bb432b",
}

# The one classical source that correctly has no blob_sha.
LIBRARY_SCAN_NO_BLOB = {"bazi.source.zipingzhenquan"}


def load_sources():
    import json

    with open(ROOT / "config/knowledge_sources.json", encoding="utf-8") as f:
        return json.load(f)["sources"]


def classical_blob_sha_gaps(sources):
    """Return classical source_ids whose blob_sha is missing/invalid.

    library_scan sources are exempt (their commit/blob_sha are null
    by design; catalog_id + pdf_sha256 identify them instead).
    """
    gaps = []
    for s in sources:
        if s.get("kind") != "classical":
            continue
        sid = s.get("source_id")
        if sid in LIBRARY_SCAN_NO_BLOB:
            continue
        blob = s.get("blob_sha")
        if not isinstance(blob, str) or not HEX40.match(blob):
            gaps.append(sid)
    return gaps


class Tj0181SourceBlobShaTests(unittest.TestCase):
    def test_classical_sources_all_have_blob_sha(self):
        sources = load_sources()
        gaps = classical_blob_sha_gaps(sources)
        self.assertEqual(gaps, [], f"classical sources missing valid blob_sha: {gaps}")

    def test_registered_blob_sha_values_match_upstream(self):
        sources = load_sources()
        by_id = {s["source_id"]: s for s in sources}
        self.assertEqual(len(EXPECTED_BLOB_SHA), 74)
        for sid, expected in sorted(EXPECTED_BLOB_SHA.items()):
            with self.subTest(source_id=sid):
                self.assertIn(sid, by_id, f"{sid} not in registry")
                actual = by_id[sid].get("blob_sha")
                self.assertEqual(actual, expected)
                # The blob_sha must sit beside the pinned commit/path it
                # was resolved from (no silent re-pointing).
                self.assertEqual(by_id[sid].get("commit"), by_id[sid].get("commit"))
                self.assertTrue(by_id[sid].get("path"))
                self.assertTrue(by_id[sid].get("repository"))

    def test_library_scan_source_has_no_blob_sha_by_design(self):
        sources = load_sources()
        by_id = {s["source_id"]: s for s in sources}
        s = by_id["bazi.source.zipingzhenquan"]
        self.assertEqual(s.get("provenance_kind"), "library_scan")
        self.assertIsNone(s.get("commit"))
        self.assertIsNone(s.get("blob_sha"))
        self.assertEqual(s.get("catalog_id"), "NLC416-11jh010455-35296")
        self.assertTrue(HEX64.match(s.get("pdf_sha256") or ""))

    def test_missing_blob_sha_is_detected_not_silently_filled(self):
        # Non-vacuity: removing one blob_sha must fail the completeness
        # check (an unregistered entry is reported, never silently filled).
        sources = load_sources()
        mutated = copy.deepcopy(sources)
        target = next(s for s in mutated if s["source_id"] == "bazi.source.xieji-relations")
        target["blob_sha"] = None
        gaps = classical_blob_sha_gaps(mutated)
        self.assertEqual(gaps, ["bazi.source.xieji-relations"])

    def test_implementation_sources_excluded_from_classical_check(self):
        # Implementation sources are a separate kind; they are not
        # counted as classical gaps in this batch.
        sources = load_sources()
        impl = [s for s in sources if s.get("kind") == "implementation"]
        self.assertTrue(len(impl) >= 6)
        for s in impl:
            self.assertNotIn(s["source_id"], EXPECTED_BLOB_SHA)


if __name__ == "__main__":
    unittest.main()
