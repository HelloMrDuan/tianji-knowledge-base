"""TJ-011.2 F3/F4 adjudication register: public structural contracts.

The F3 (Bing x Si, lu month) and F4 (Bing x Yin, changsheng /
generating month) morphology adjudications are DESIGN registers: they
implement no predicate. These tests pin the register's structure -
condition inventories with per-condition anchor types (a governance
convention must never be labeled original text), the shape-rejection
proofs, the satisfiability scan records, the F4 implementation gate
(both readings registered, neither selected), the Ding dispositions,
the earth-root interface audit, the cross-register quote references,
and the Golden designs (real charts only, legal pillars, expectations
consistent with their condition tables).

Byte-for-byte quote verification against the sealed snapshots and
real-chart replay through the production calendar chain live in
test_tj0112_f34_si_yin_sealed.py (offline acceptance only, NOT public
CI, same partition rule as the earlier batches).
"""
import ast
import json
import pathlib
import unittest

from tianji_kb import bazi_fire_si_yin_morphology as f34

ROOT = pathlib.Path(__file__).resolve().parents[1]
STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'


class TestRegisterIdentity(unittest.TestCase):
    def test_register_block(self):
        reg = f34.F34_ADJUDICATION_REGISTER
        self.assertEqual(
            reg['id'], 'bazi-fire-si-yin-morphology-adjudication-v1')
        self.assertEqual(reg['task'], 'TJ-011.2')
        snap = reg['source_snapshot']
        self.assertEqual(
            snap['ditiansui_sha256'],
            '6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795')
        self.assertEqual(snap['ditiansui_chars'], 139538)
        self.assertEqual(
            snap['sanming_sha256'],
            '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86')
        self.assertEqual(snap['sanming_chars'], 461157)

    def test_module_defines_no_functions(self):
        tree = ast.parse(pathlib.Path(f34.__file__).read_text('utf-8'))
        functions = [n.name for n in ast.walk(tree)
                     if isinstance(n, (ast.FunctionDef,
                                       ast.AsyncFunctionDef))]
        self.assertEqual(functions, [])

    def test_supersede_relation_keeps_f1_history(self):
        sup = f34.F34_ADJUDICATION_REGISTER['supersedes_dispositions']
        self.assertEqual(sup['register'], 'bazi_fire_morphology')
        self.assertEqual(sup['entries'], {
            'F3': 'not_adjudicated',
            'F4': 'deferred_not_adjudicated',
        })

    def test_dispositions(self):
        self.assertEqual(f34.F34_DISPOSITIONS, {
            'F3': {
                'subject': 'fire x Si month strong (lu month)',
                'disposition': 'adjudicated_buildable_new_form',
                'form_id': 'bing-si-lu-commanding-visible-support-v1',
                'implementation': 'not_in_this_batch',
            },
            'F4': {
                'subject': 'fire x Yin month strong (changsheng / '
                           'generating month)',
                'disposition': 'adjudicated_design_implementation_gated',
                'form_id': 'bing-yin-changsheng-visible-support-v1',
                'implementation': 'blocked_pending_siling_expansion_'
                                   'user_adjudication',
            },
            'DING_SI': {
                'subject': 'ding x Si',
                'disposition': 'blocked_by_conflict',
                'conflict_id': 'sanming-juan2.ding-changsheng',
            },
            'DING_YIN': {
                'subject': 'ding x Yin',
                'disposition': 'blocked_by_conflict',
                'conflict_id': 'sanming-juan2.ding-changsheng',
            },
        })


class TestFormStructure(unittest.TestCase):
    def _check_form(self, form, month_key, convention_id):
        self.assertEqual(form['day_master'], '丙')
        self.assertEqual(form['direction'], 'strong')
        keys = [c['key'] for c in form['conditions']]
        self.assertEqual(len(keys), 9)
        self.assertEqual(keys[1], month_key)
        for cond in form['conditions']:
            self.assertIn(cond['anchor_type'], {
                'original_text', 'governance_convention',
                'framework_derived', 'scope_construction'})
            self.assertTrue(cond['statement'])
        by_key = {c['key']: c for c in form['conditions']}
        # The month condition must be original text, never a
        # convention or a derivation.
        self.assertEqual(by_key[month_key]['anchor_type'],
                         'original_text')
        self.assertTrue(by_key[month_key]['anchors'])
        # The hidden-layer condition must be disclosed as governance.
        hidden = by_key['hidden_layer_convention_applied']
        self.assertEqual(hidden['anchor_type'], 'governance_convention')
        self.assertEqual(hidden['convention'], convention_id)
        # No condition in either form is framework_derived: both
        # month positions rest on per-stem listed sentences.
        self.assertNotIn('framework_derived',
                         {c['anchor_type'] for c in form['conditions']})
        self.assertEqual(form['evidence_binding'],
                         'pending_phase1_rule_registration')
        self.assertIs(form['research_only'], True)
        self.assertIs(form['public_enabled'], False)
        self.assertIs(form['ai_enabled'], False)
        excl = form['exclusions']
        for name in ('visible_officer', 'visible_killer',
                     'visible_wealth', 'visible_output'):
            self.assertEqual(excl[name]['verdict'], 'excluded')
        self.assertEqual(
            excl['hidden_officer_killer_wealth_output']['verdict'],
            'recorded_not_adjudicated_outside_scope')

    def test_form_bing_si(self):
        self._check_form(f34.FORM_BING_SI, 'reviewed_lu_command_month',
                         'fire-morph.wu-geng-in-si-non-veto')
        self.assertEqual(f34.FORM_BING_SI['form_id'],
                         'bing-si-lu-commanding-visible-support-v1')
        self.assertEqual(f34.FORM_BING_SI['month_branch'], '巳')
        self.assertEqual(f34.FORM_BING_SI['scope_candidate'],
                         'lu_visible_support')

    def test_form_bing_yin(self):
        self._check_form(f34.FORM_BING_YIN,
                         'reviewed_generating_changsheng_month',
                         'fire-morph.wu-in-yin-non-veto')
        self.assertEqual(f34.FORM_BING_YIN['form_id'],
                         'bing-yin-changsheng-visible-support-v1')
        self.assertEqual(f34.FORM_BING_YIN['month_branch'], '寅')
        # F4 must never claim commanding.
        self.assertIn('NONE', f34.FORM_BING_YIN['commanding_claim'])

    def test_condition_keys_align_across_forms(self):
        si = [c['key'] for c in f34.FORM_BING_SI['conditions']]
        yin = [c['key'] for c in f34.FORM_BING_YIN['conditions']]
        diff = [(a, b) for a, b in zip(si, yin) if a != b]
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][0], 'reviewed_lu_command_month')
        self.assertEqual(diff[0][1],
                         'reviewed_generating_changsheng_month')

    def test_hidden_convention_instances(self):
        si = f34.F3_HIDDEN_CONVENTION_INSTANCE
        yin = f34.F4_HIDDEN_CONVENTION_INSTANCE
        self.assertEqual(si['id'], 'fire-morph.wu-geng-in-si-non-veto')
        self.assertEqual(yin['id'], 'fire-morph.wu-in-yin-non-veto')
        for inst in (si, yin):
            self.assertEqual(inst['anchor_type'],
                             'governance_convention')
            self.assertTrue(inst['scope_limit'])


class TestShapeRejections(unittest.TestCase):
    def test_f3_rejections(self):
        rej = f34.F3_SHAPE_REJECTIONS
        self.assertEqual(rej['pure_support_shape']['verdict'],
                         'constructively_unsatisfiable')
        self.assertEqual(
            rej['pure_generating_support_shape']['verdict'],
            'name_relation_mismatch')
        self.assertEqual(
            rej['commanding_form_month_extension']['verdict'],
            'rejected_scope_widening')
        for entry in rej.values():
            self.assertTrue(entry['proof'])

    def test_f4_rejections(self):
        rej = f34.F4_SHAPE_REJECTIONS
        self.assertEqual(rej['pure_support_shape']['verdict'],
                         'constructively_unsatisfiable')
        self.assertEqual(
            rej['pure_generating_support_shape']['verdict'],
            'constructively_unsatisfiable')
        self.assertEqual(rej['pure_month_name']['verdict'],
                         'name_relation_mismatch')


class TestSatisfiabilityRecords(unittest.TestCase):
    def test_f3_scan_record(self):
        sat = f34.F3_SATISFIABILITY
        self.assertEqual(sat['verdict'],
                         'satisfiable_single_witness_in_scan_range')
        self.assertEqual(sat['scan']['chart_count'], 7512)
        self.assertEqual(sat['scan']['positive_count'], 1)
        self.assertIn('1927-05-12', sat['scan']['witness'])

    def test_f4_scan_record(self):
        sat = f34.F4_SATISFIABILITY
        self.assertEqual(sat['verdict'], 'satisfiable_all_segments')
        self.assertEqual(sat['scan']['chart_count'], 7164)
        self.assertEqual(sat['scan']['positive_count'], 39)
        self.assertEqual(sat['scan']['segment_distribution'],
                         {'戊': 12, '丙': 8, '甲': 19})


class TestImplementationGate(unittest.TestCase):
    def test_gate_registered_openly(self):
        gate = f34.F4_IMPLEMENTATION_GATE
        self.assertEqual(
            gate['status'],
            'implementation_blocked_pending_user_adjudication')
        self.assertIs(gate['adjudication_blocked'], False)
        readings = {r['id']: r for r in gate['readings']}
        self.assertEqual(set(readings),
                         {'principal_only', 'segment_tightened'})
        for reading in readings.values():
            self.assertEqual(reading['status'], 'registered_not_selected')
        self.assertIn('Neither reading may be implemented alone',
                      gate['rule'])


class TestDingDispositions(unittest.TestCase):
    def test_ding_si(self):
        disp = f34.DING_SI_DISPOSITION
        self.assertEqual(disp['verdict'], 'blocked_by_conflict')
        self.assertEqual(disp['conflict_id'],
                         'sanming-juan2.ding-changsheng')
        self.assertTrue(any('lu' in n or '禄' in n or 'Wu' in n
                            for n in disp['structural_notes']))

    def test_ding_yin(self):
        disp = f34.DING_YIN_DISPOSITION
        self.assertEqual(disp['verdict'], 'blocked_by_conflict')
        self.assertEqual(disp['conflict_id'],
                         'sanming-juan2.ding-changsheng')


class TestEarthRootInterface(unittest.TestCase):
    def test_audit(self):
        iface = f34.EARTH_ROOT_INTERFACE
        self.assertIn('does not block', iface['audit_conclusion'])
        audited = {row['condition'] for row in
                   iface['per_condition_audit']}
        self.assertIn('visible_positions_support_only', audited)
        self.assertIn('all_visible_have_reviewed_roots', audited)
        self.assertIn('effective_heavy_day_roots', audited)
        for row in iface['per_condition_audit']:
            self.assertTrue(row['note'])
        self.assertTrue(iface['pending_surface'])
        self.assertTrue(iface['contrast_with_s2_metal'])


class TestQuoteReferences(unittest.TestCase):
    def test_all_references_resolve_to_known_registers(self):
        known = {'bazi_fire_morphology',
                 'bazi_sanming_juan2_collation', 'bazi_siling_matrix'}
        for ref, entry in f34.QUOTE_REFERENCES.items():
            self.assertIn(entry['register'], known, ref)
            self.assertTrue(entry['role'], ref)

    def test_key_references_present(self):
        for ref in ('dt.congqiang_def', 'dt.congwang_def',
                    'dt.congqiang_no_caiguan', 'dt.root_heavy_light',
                    'sm2.bing_lu', 'sm2.bing_sheng', 'sm2.renyuan_bing',
                    'dt.s024_yinyue', 'sf.lubiao', 'dt.bing_lu_single'):
            self.assertIn(ref, f34.QUOTE_REFERENCES)

    def test_anchor_refs_used_by_forms_are_registered(self):
        for form in (f34.FORM_BING_SI, f34.FORM_BING_YIN):
            for anchor in form['definition_anchors']:
                self.assertIn(anchor['quote_ref'],
                              f34.QUOTE_REFERENCES)
            for cond in form['conditions']:
                for ref in cond.get('anchors', []):
                    self.assertIn(ref, f34.QUOTE_REFERENCES)
            for excl in form['exclusions'].values():
                for ref in excl.get('anchors', []):
                    self.assertIn(ref, f34.QUOTE_REFERENCES)


class TestGoldenDesigns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.golden = json.loads(
            (ROOT / 'tests' / 'golden_tj0112_f34_si_yin.json')
            .read_text('utf-8'))
        cls.cases = {c['id']: c for c in cls.golden['cases']}

    def test_seven_cases_five_three_two_split(self):
        self.assertEqual(len(self.cases), 7)
        f3 = [c for c in self.cases.values() if c['form'] == 'F3']
        f4 = [c for c in self.cases.values() if c['form'] == 'F4']
        self.assertEqual(len(f3), 5)
        self.assertEqual(len(f4), 2)
        cats = {c['category'] for c in self.cases.values()}
        self.assertEqual(cats, {'positive', 'near_miss_single_condition',
                                'abstain_unknown', 'conflict_registered',
                                'counterexample', 'gate_sensitivity'})

    def test_pillars_are_legal_ganzhi(self):
        for case in self.cases.values():
            self.assertEqual(len(case['expected_pillars']), 4)
            for pillar in case['expected_pillars']:
                self.assertEqual(len(pillar), 2)
                self.assertIn(pillar[0], STEMS)
                self.assertIn(pillar[1], BRANCHES)
                # Legal pillar: stem and branch share parity.
                self.assertEqual(STEMS.index(pillar[0]) % 2,
                                 BRANCHES.index(pillar[1]) % 2,
                                 f'{case["id"]}: {pillar}')

    def test_day_master_and_month_per_form(self):
        for case in self.cases.values():
            day, month = (case['expected_pillars'][2],
                          case['expected_pillars'][1])
            self.assertEqual(day[0], '丙', case['id'])
            self.assertEqual(month[1],
                             '巳' if case['form'] == 'F3' else '寅',
                             case['id'])

    def test_condition_tables_consistent_with_expectations(self):
        forms = {'F3': f34.FORM_BING_SI, 'F4': f34.FORM_BING_YIN}
        for case in self.cases.values():
            keys = {c['key'] for c in
                    forms[case['form']]['conditions']}
            table = case['expected_conditions']
            self.assertEqual(set(table), keys, case['id'])
            failed = {k for k, v in table.items() if not v}
            self.assertEqual(failed,
                             set(case['expect']['failed_conditions']),
                             case['id'])
            # Flipped by the F3 implementation batch (E0248): the F3
            # scan-witness positive now classifies strong through the
            # lu_visible_support predicate; every other case's engine
            # verdict is unchanged (F4 still gated on the siling
            # expansion adjudication).
            expected_engine = (
                'strong' if case['id']
                == 'tj0112-f3-positive-scan-witness'
                else 'indeterminate')
            self.assertEqual(case['expect']['current_engine'],
                             expected_engine, case['id'])

    def test_positive_cases_all_conditions_true(self):
        for case in self.cases.values():
            if case['category'] == 'positive':
                self.assertTrue(
                    all(case['expected_conditions'].values()),
                    case['id'])

    def test_near_miss_fails_exactly_the_rootedness_condition(self):
        case = self.cases['tj0112-f3-near-miss-unrooted-resource']
        self.assertEqual(case['expect']['failed_conditions'],
                         ['all_visible_have_reviewed_roots'])

    def test_conflict_case_carries_registered_conflict(self):
        case = self.cases['tj0112-f3-conflict-xu-root']
        self.assertEqual(case['expect']['conflict_ids'],
                         ['bazi.concept.conflict_root_type_readings'])
        self.assertIs(case['expect']['conflict_blocking'], True)

    def test_gate_case_registers_both_readings(self):
        case = self.cases['tj0112-f4-gate-sensitivity-first-segment']
        self.assertEqual(case['expect']['commander_segment'], '戊')
        self.assertEqual(case['expect']['readings'], {
            'principal_only': 'satisfied',
            'segment_tightened': 'month_condition_false',
        })
        self.assertEqual(case['expect']['design_classification'],
                         'undetermined_pending_segment_decision')
        pos = self.cases['tj0112-f4-positive-both-readings']
        self.assertEqual(pos['expect']['commander_segment'], '甲')
        self.assertEqual(pos['expect']['readings'], {
            'principal_only': 'satisfied',
            'segment_tightened': 'satisfied',
        })


if __name__ == '__main__':
    unittest.main()
