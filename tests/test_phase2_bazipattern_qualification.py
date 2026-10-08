"""Boundary tests: commander review and pattern *qualification*, never 定格."""
import unittest

from tianji_kb.bazi_commander import COMMAND_VARIANT, MONTH_BRANCHES, commander_review_matrix
from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart


def qualification(out, family):
    return out['result']['pattern_candidates'][family]['qualification']


class PatternQualificationTests(unittest.TestCase):
    def run_chart(self, *pillars, **opts):
        return chart(*pillars, pattern_variant=PATTERN_VARIANT, **opts)

    def test_all_twelve_months_are_scoped_without_false_resolution(self):
        rows = commander_review_matrix()
        self.assertEqual(len(rows), 12)
        self.assertEqual({r['month_branch'] for r in rows}, set(MONTH_BRANCHES))
        reviewed = {r['month_branch']: r for r in rows}
        self.assertEqual(reviewed['寅']['source_comparison_status'], 'source_conflict')
        self.assertEqual(len(reviewed['寅']['candidate_profiles']), 2)
        self.assertEqual(reviewed['寅']['dated_boundary_status'], 'insufficient_text')
        for month in set(MONTH_BRANCHES) - {'寅'}:
            self.assertEqual(reviewed[month]['candidate_review_status'], 'not_reviewed')
            self.assertEqual(reviewed[month]['source_comparison_status'], 'not_reviewed')
            self.assertEqual(reviewed[month]['dated_boundary_status'], 'not_reviewed')
        for month in ('辰', '戌', '丑', '未'):
            self.assertEqual(reviewed[month]['principal_qi_status'], 'not_reviewed')
        for row in rows:
            self.assertEqual(row['commander_status'], 'unresolved')
            self.assertIsNone(row['exact_day_commander'])

    def test_twelve_runtime_months_preserve_review_status(self):
        months = ('丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未',
                  '壬申', '癸酉', '甲戌', '乙亥', '丙子', '丁丑')
        matrix = {r['month_branch']: r for r in commander_review_matrix()}
        for month_gz in months:
            with self.subTest(month=month_gz):
                out = chart('甲子', month_gz, '甲子', '乙丑',
                            month_command_variant=COMMAND_VARIANT)
                command = out['result']['month_command_variant']
                self.assertEqual(command['dated_review'], matrix[month_gz[1]])
                self.assertIsNone(command['commander'])
                self.assertEqual(command['commander_status'], 'unresolved')

    def test_official_and_resource_qualification_remains_indeterminate(self):
        official = self.run_chart('戊午', '辛酉', '甲午', '庚午')
        row = qualification(official, 'official')
        self.assertEqual(row['qualification_status'], 'indeterminate')
        self.assertEqual(row['family_determination_status'], 'unresolved')
        req = {r['id']: r for r in row['requirements']}
        self.assertEqual(req['monthly_hidden_stem_candidate']['status'], 'observed')
        self.assertEqual(req['literal_exposure']['status'], 'observed')
        self.assertEqual(req['dated_commander']['status'], 'unresolved')
        self.assertEqual(req['family_specific_competing_conditions']['status'], 'unresolved')
        resource = self.run_chart('癸亥', '壬子', '甲寅', '癸酉')
        self.assertEqual(qualification(resource, 'resource')['qualification_status'], 'indeterminate')
        self.assertTrue(qualification(resource, 'resource')['evidence_ids'])

    def test_no_candidate_rejects_only_month_hidden_route(self):
        out = self.run_chart('辛酉', '丙寅', '甲子', '庚午')
        q = qualification(out, 'official')
        self.assertEqual(q['qualification_status'], 'disqualified_for_this_branch')
        self.assertEqual(q['branch'], 'monthly_hidden_stem_observation_only')
        self.assertEqual(q['family_determination_status'], 'unresolved')
        self.assertEqual(out['result']['pattern_candidates']['official']['determination']['status'], 'unresolved')
        self.assertIsNone(out['result']['pattern_candidates']['official']['determination']['pattern'])

    def test_exposure_miscellaneous_and_source_conflict_do_not_determine_pattern(self):
        unexposed = qualification(self.run_chart('戊午', '丁酉', '甲午', '丙午'), 'official')
        self.assertEqual(unexposed['qualification_status'], 'indeterminate')
        self.assertEqual(next(r for r in unexposed['requirements'] if r['id']=='literal_exposure')['status'], 'not_observed')
        mixed = qualification(self.run_chart('辛酉', '丁丑', '甲子', '癸亥'), 'resource')
        self.assertTrue(next(r for r in mixed['requirements'] if r['id']=='luren_miscellaneous_month_exceptions')['known_miscellaneous_branch'])
        conflicted = qualification(self.run_chart('甲子', '丙寅', '丙午', '乙亥'), 'resource')
        self.assertEqual(next(r for r in conflicted['requirements'] if r['id']=='dated_commander')['status'], 'source_conflict')
        self.assertIn('bazi.concept.conflict_siling_days', conflicted['conflict_ids'])

    def test_fact_pointers_and_evidence_are_real(self):
        out = self.run_chart('戊午', '辛酉', '甲午', '庚午')
        q = qualification(out, 'official')
        for eid in q['evidence_ids']:
            self.assertIn(eid, out['evidence'])
        for requirement in q['requirements']:
            for pointer in requirement['fact_refs']:
                item = out
                for token in pointer.removeprefix('#/').split('/'):
                    item = item[int(token)] if isinstance(item, list) else item[token]
                self.assertIsNotNone(item)
        self.assertTrue(q['research_only'])
        self.assertFalse(q['public_enabled'])
        self.assertFalse(q['ai_enabled'])

    def test_datetime_input_does_not_claim_dated_commander(self):
        out = execute('bazi', {'value': '2026-02-10T12:00:00+08:00',
                               'pattern_variant': PATTERN_VARIANT}, allow_research=True)
        row = out['result']['pattern_candidates']['resource']
        self.assertEqual(row['dated_commander']['status'], 'unresolved')
        self.assertEqual(row['qualification']['family_determination_status'], 'unresolved')
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])


if __name__ == '__main__':
    unittest.main()
