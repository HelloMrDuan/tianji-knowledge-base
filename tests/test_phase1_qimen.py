import json
import shutil
import subprocess
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from lunar_python import Solar
from tianji_kb.operations.qimen import *

ROOT = Path(__file__).resolve().parents[1]
class QimenPhase1Tests(unittest.TestCase):
    def test_bureau_and_classical_yuan(self):
        self.assertEqual(bureau('冬至','甲子')['bureau'],1)
        self.assertEqual(bureau('冬至','己巳')['bureau'],7)
        self.assertEqual(bureau('冬至','甲戌')['bureau'],4)
        self.assertEqual(bureau('夏至','甲子')['dun'],'阴')
        with self.assertRaises(ValueError):
            bureau('unknown','甲子')

    def test_all_bureaus_preserve_nine_stems_and_eight_symbols(self):
        for dun in ['阴','阳']:
            for number in range(1,10):
                self.assertEqual(set(earth_plate(dun,number).values()),set('戊己庚辛壬癸丁丙乙'))
        for term,_,_ in base()['solar_term_bureaus']:
            for day in ['甲子','己巳','甲戌']:
                for hour in ['甲子','乙丑','癸酉']:
                    chart=chart_from_calendar(term,day,hour)
                    self.assertEqual(len({x for x in chart['doors'].values() if x}),8)
                    self.assertEqual(len({x for x in chart['deities'].values() if x}),8)
                    self.assertEqual(chart['deities']['5'],'')

    @unittest.skipUnless(shutil.which('node'),'Node oracle unavailable')
    def test_transferred_plate_operations_match_fixed_upstream_modules(self):
        snapshot=ROOT/next(s['content_path'] for s in json.loads((ROOT/'config/knowledge_sources.json').read_text())['sources'] if s['source_id']=='qimen.source.qfdk-implementation')
        snapshot=snapshot.parent
        cases=[]
        for term in ['冬至','夏至']:
            for day in ['甲子','己巳','甲戌']:
                for hour in ['甲子','乙丑','戊辰','癸酉']:
                    cases.append([term,day,hour])
        program='''const p=process.argv[1];const cases=JSON.parse(process.argv[2]);const d=require(p+'/dipan');const x=require(p+'/jiuxing');const m=require(p+'/bamen');const s=require(p+'/bashen');let out=[];for(const c of cases){const earth=d.getDiPan(c.type,c.num);const stars=x.distributeJiuXing(earth,c.instrument,c.hour[0]);const doors=m.distributeBaMen(stars.zhiFuGong,c.hour,c.type);const gods=s.distributeBaShen(stars.zhiFuLuoGong,c.type);out.push({earth,stars:stars.jiuXing,doors:doors.baMen,gods});}process.stdout.write(JSON.stringify(out));'''
        charts=[chart_from_calendar(*case) for case in cases]
        args=[{'type':'yang' if c['dun']=='阳' else 'yin','num':c['bureau'],'instrument':'戊己庚辛壬癸'[ganzhi_index(c['hour_ganzhi'])//10],'hour':c['hour_ganzhi']} for c in charts]
        expected=json.loads(subprocess.check_output(['node','-e',program,str(snapshot),json.dumps(args,ensure_ascii=False)],text=True))
        for chart,oracle in zip(charts,expected):
            for our,their in [('earth_plate','earth'),('stars','stars'),('doors','doors'),('deities','gods')]:
                self.assertEqual(chart[our],oracle[their])

    def test_exact_solar_term_boundary_and_timezone_equivalence(self):
        lunar=Solar.fromYmdHms(2026,6,21,12,0,0).getLunar()
        boundary=lunar.getJieQiTable()['夏至']
        instant=datetime.fromisoformat(boundary.toYmdHms()).replace(tzinfo=ZoneInfo('Asia/Shanghai'))
        self.assertEqual(calendar_from_datetime(instant-timedelta(seconds=1))['solar_term'],'芒种')
        self.assertEqual(calendar_from_datetime(instant)['solar_term'],'夏至')
        self.assertEqual(chart_from_datetime(instant)['dun'],'阴')
        self.assertEqual(chart_from_datetime(instant),chart_from_datetime(instant.astimezone(ZoneInfo('UTC'))))
        with self.assertRaises(ValueError):
            chart_from_datetime(datetime(2026,6,21))
        with self.assertRaises(ValueError):
            chart_from_calendar('冬至','甲子','甲子','置闰')
