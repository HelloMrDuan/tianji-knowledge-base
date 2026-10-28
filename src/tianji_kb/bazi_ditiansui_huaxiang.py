"""滴天髓阐微《化象》章整章登记（TJ-012.3 证据登记批：E0270 待办 B4 落实）。

背景：合化审定批（E0270）盘点确认，
已登记的合化条件材料全部在三命一家之内；滴天髓《化象》章（原注＋
任氏曰两套真化条件）此前只有 docs/product/BAZI_PATTERN_AUDIT.md 审计
条目 P05 在案、未登记（该册缺口 B4），其 F5/F6 两条只记结构与缺口、
不得作引文消费。本批按渊海正官组登记（E0237）的体例把该章逐字落入
滴天髓 review_scope：整章 [98297, 99943) 全文登记（1646 字），按章题
句/原注/任氏曰/任氏例造四层分段（13 段平铺整章，段间空白填充在册），
引文 19 条逐条登记（层属分开标注、字符定位、全文计数 ==1），章内字
形/语义疑点 10 项逐项落账（逐字保留、mapped_reading 全 None）。

登记结论只及于结构：原注（F5）与任氏曰（F6）两套真化条件的要素构成
逐项登记并附引文为据（要素词汇沿 E0270 的 11 要素，另加两层共有的
化后作用面 huashen_xiji）；两套表述与三命 F1–F4 的关系只登记「同题
异述」事实，不做冲突裁定、不并入 E0270 的冲突结构（C1–C5 结论不
变）；本章题名「化象」而内容为干合化气条件，与三命卷六《化象》的从
化象 doctrine 是不同裁定对象，P-D1（化气）/P-D2（从化象）的分开登
记保持不变。

本模块是纯数据登记，**零判定代码**：不产出任何从化/化气/化格判定，
determination 面零变化，transformation_status 恒 unresolved。引文全
部经机上密封快照切片逐字复核。Canonical/Phase1 注册状态 pending
（与既有研究级登记同口径披露）。
"""

HUAXIANG_ID = 'bazi-ditiansui-huaxiang-registration-v1'

HUAXIANG_TASK = 'TJ-012.3 (ditiansui huaxiang chapter registration; E0270 pending item B4)'

DITIANSHUI_SNAPSHOT = {
 'file': 'ditiansui_chanwei.txt',
 'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/ditiansui_chanwei.txt',
 'sha256': '6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795',
 'blob_sha': 'ae45f40a8f7de7806e0f9fdf6fd952b8a6148467',
 'bytes': 368684,
 'chars': 139538
}

HUAXIANG_CHAPTER = {
 'section_id': 'ditiansui.huaxiang',
 'title': '十三、化象',
 'source_id': 'bazi.source.ditiansui-spouse',
 'locator': {
  'char_start': 98297,
  'char_end': 99943
 },
 'title_locator': {
  'char_start': 98297,
  'char_end': 98302
 },
 'registration_mode': 'full_chapter',
 'audit_ref': 'docs/product/BAZI_PATTERN_AUDIT.md P05',
 'full_text': '十三、化象\n化得真者只论化,化神还有几般话。\n原注:如甲日主生于四季,单遇一位已土,在月时上合遇壬、癸、甲、乙、戊,而有一辰字,乃为化得真。又如丙辛生于冬月,戊癸生于夏月,乙庚生于秋月,丁壬生于春月,独自相合,又得龙以运之,此为真化矣。既化矣,又论化神。如甲己化土,土阴寒,要火气昌旺;土太旺,又要取水为财,木为官,金为食神 。随其所向,论其喜忌,再见甲乙,亦不作争合妒合论。盖真化矣,如烈女不更二夫,岁运遇之皆闲神也。\n任氏曰:合化之原,昔黄帝礼天于圜邱,天降十干,爱命大挠作十二支以配之。故日干曰天干,其所由,合即天一、地二、天三、地四、天五、地六、天七、地八、天九、地十之义。依数推之,则甲一、乙二、丙三、丁四、戊五、己六、庚七、辛八、壬九、癸十也。如“洛书”以五居中,一得五为六,故甲与己合;二得五为七,故乙与庚合;三得五为八,故丙与辛合;四得五为九,故丁与壬合;五得五为十,故戊与癸合。合则化,化亦必得五土而后成,五土者辰也。辰土居春,时在三阳,生物之体,气辟而动,动则变,变则化矣。且十干之合,而至五辰之位,则化气之元神发露。故甲己起甲子,至五位逢戊辰而化土;乙庚到丙子,至五位逢庚辰而化金;丙辛起戊子,至五位逢壬辰而化水;丁壬起庚子,至五位逢甲辰而化木;戊癸起壬子,至五位逢丙辰而化火。此相合相化之真源,近世得传者少,只知逢龙而化,不知逢五而化,辰龙之说,供引之意,如果辰为真龙。则辰年生人为龙,可行雨,而寅年生人为虎,必伤人矣。至于化象作用,亦有喜忌配合之理,所以“化神还有几般话”也。非化斯神,喜见斯神,执一而论也,是化象亦要究其衰旺,审其虚实,察其喜忌,则吉凶有验,否泰了然矣。如化神旺而有余,宜泄化神之神为用;化神衰而不足,宜生助化神之神为用。如甲己化土,生于未戌月,土燥而旺,干透丙丁,支藏巳午。谓之有余,再行火土之运,必太过而不吉也。须从其意向,柱中有水,要行金运;柱中有金,要行水运;无金无水,土势太旺,秘要金泄之;火土过燥,要带水之金运以润之。生于丑辰月,土湿为弱,火虽有虚,水木无而实,或干支杂其金水,谓之不足,亦须从其意向。柱中有金,要行火运;柱中有水,要行土运;金水并见,过于虚湿,要带火之土运以实之,助起化神为吉也。至于争合妒合之说,乃谬论也,既合而化,如贞妇配义夫,从一而终,不生二心,见戊己是彼之同类,遇甲乙是我之本气,有相让之谊。合而不化,勉强之意,必非佳偶。见戊己多而起争妒之风,遇甲乙众而更强弱之性。甲己之合如此,余可类推。\n乙丑\n甲申\n甲辰\n己巳癸未\n壬午\n辛巳\n庚辰\n己卯\n戊寅\n年月两干之甲乙,得当令之申金、丑内之辛金制化,不起争妒之风。时干己土临旺,与日主亲切而合,合神真实,乃谓真化。但秋金当令,化神泄气不足。至午运助化神,中乡榜;辛巳金火土并旺,癸黄甲,宴琼林,入翰苑,仕黄堂,庚辰合乙制化比劫,仕至藩臬。\n \n \n \n戊辰\n壬戌\n甲辰\n己巳癸亥\n甲子\n乙丑\n丙寅\n丁卯\n戊辰\n甲木生于季秋,土旺乘权,克去壬水,又无比劫,合神更真,化气有余。惜运走东北水木之地,功名仕路,不及前造,至丑运丁酉年,暗会金局,泄化神而吐秀,登科;戊戌年发甲,仕至州牧。\n \n \n \n \n己卯\n丁卯\n壬午\n甲辰丙寅\n乙丑\n甲子\n癸亥\n壬戌\n辛酉\n壬水生于仲春,化象斯真。最喜甲木元神透露,化气有余。余则宜泄,斯化神吐秀,喜其坐下午,午生辰土,秀气流行。少年科甲,翰苑名高,惜乎中运水旺之地,未能显秩,终于县宰。\n \n \n \n \n己卯\n丁卯\n壬午\n癸卯丙寅\n乙丑\n甲子\n癸亥\n壬戌\n辛酉\n此与前造只换一卯字,化象更真,化神更有余。嫌其癸劫争财,年干己土,透隔无根,不能去其癸水。午火未能流行。此癸水,真乃夺标之客也。虽中乡榜,终不能出仕。\n \n \n \n \n丙戌\n戊戌\n癸巳\n壬戌己亥\n庚子\n辛丑\n壬寅\n癸卯\n甲辰\n癸水生于季秋,丙火透而通根,化火斯真。嫌其时透壬水克丙,只中乡榜,直至卯运,壬水绝地,挑知县,历三任而不升,亦壬水夺财之故也。\n \n \n \n ',
 'placeholder_count_in_chapter': 0,
 'pua_count_in_chapter': 0,
 'note': '整章逐字登记（1646 字）：章题＋章题句、原注整段、任氏曰整段、任氏五例造与段间空白填充全部在册；下一章「十四、假从」起于 99943（密封专项钉界）。章内半角 ? 0 处、PUA 0 处（全书 ? 共 132 处均在本章之外，本批不处理）。引文 19 条（章题句 1＋原注 4＋任氏曰 9＋例造断语 5），全部经机上快照切片逐字复核、全文计数 ==1。'
}

HUAXIANG_SEGMENTS = [
 {
  'segment_id': 'ditiansui.huaxiang.head',
  'layer': '章题＋章题句',
  'locator': {
   'char_start': 98297,
   'char_end': 98320
  },
  'title_locator': {
   'char_start': 98297,
   'char_end': 98302
  },
  'quote_ids': [
   'hx.head_verse'
  ],
  'note': '章题「十三、化象」[98297,98302)＋换行＋章题句 [98303,98319)＋换行；章题句即审计条目 P05 的锚点引文（锚点 98303）。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.yuanzhu',
  'layer': '原注',
  'locator': {
   'char_start': 98320,
   'char_end': 98508
  },
  'layer_marker': {
   'text': '原注:',
   'locator': {
    'char_start': 98320,
    'char_end': 98323
   }
  },
  'quote_ids': [
   'hx.yuanzhu_jiaji_cond',
   'hx.yuanzhu_four_pairs_cond',
   'hx.yuanzhu_huashen_frame',
   'hx.yuanzhu_zhengdu'
  ],
  'note': '原注整段：层属标记「原注:」位于 [98320,98323)（半角冒号，快照原样），正文自 98323 起；含甲己例、其余四对季节月通则、化神喜忌与真化后争妒不论四层内容，引文 4 条分层登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.renshi',
  'layer': '任氏曰',
  'locator': {
   'char_start': 98508,
   'char_end': 99334
  },
  'layer_marker': {
   'text': '任氏曰:',
   'locator': {
    'char_start': 98508,
    'char_end': 98512
   }
  },
  'quote_ids': [
   'hx.renshi_origin',
   'hx.renshi_luoshu_pairs',
   'hx.renshi_fengwu',
   'hx.renshi_fenglong_critique',
   'hx.renshi_xiji_frame',
   'hx.renshi_yushe_yubu',
   'hx.renshi_yushe_example',
   'hx.renshi_buzu_example',
   'hx.renshi_zhengdu'
  ],
  'note': '任氏曰整段：层属标记「任氏曰:」位于 [98508,98512)（半角冒号，快照原样），正文自 98512 起；含合化之原（数合/洛书）、逢五而化与逢龙批判、化象作用喜忌（有余/不足两例）、争合妒合谬论四层内容，引文 9 条分层登记。本段之后的五例造同属任氏层（例造段），分开登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.example_1',
  'layer': '任氏曰（例造）',
  'locator': {
   'char_start': 99334,
   'char_end': 99481
  },
  'chart_lines': [
   {
    'text': '乙丑',
    'locator': {
     'char_start': 99334,
     'char_end': 99336
    }
   },
   {
    'text': '甲申',
    'locator': {
     'char_start': 99337,
     'char_end': 99339
    }
   },
   {
    'text': '甲辰',
    'locator': {
     'char_start': 99340,
     'char_end': 99342
    }
   },
   {
    'text': '己巳癸未',
    'locator': {
     'char_start': 99343,
     'char_end': 99347
    }
   },
   {
    'text': '壬午',
    'locator': {
     'char_start': 99348,
     'char_end': 99350
    }
   },
   {
    'text': '辛巳',
    'locator': {
     'char_start': 99351,
     'char_end': 99353
    }
   },
   {
    'text': '庚辰',
    'locator': {
     'char_start': 99354,
     'char_end': 99356
    }
   },
   {
    'text': '己卯',
    'locator': {
     'char_start': 99357,
     'char_end': 99359
    }
   },
   {
    'text': '戊寅',
    'locator': {
     'char_start': 99360,
     'char_end': 99362
    }
   }
  ],
  'commentary_quote_id': 'hx.example1_commentary',
  'note': '甲己化土例造一（断语自述年月两干甲乙、时干己土、真化）：逐行干支 9 行组（第 4 行并书两组干支）＋断语段 [99363,99480)；逐行干支为快照版式原样逐字登记，柱位/运柱的版式读法不断言（见 limitations），断语自述的柱位指称只作原文登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.filler_1',
  'layer': '空白填充',
  'locator': {
   'char_start': 99481,
   'char_end': 99487
  },
  'note': '例造间/章末的空白填充行（单空格＋换行，快照版式原样）：无文本内容，只为使分段平铺整章、逐字可复核而登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.example_2',
  'layer': '任氏曰（例造）',
  'locator': {
   'char_start': 99487,
   'char_end': 99602
  },
  'chart_lines': [
   {
    'text': '戊辰',
    'locator': {
     'char_start': 99487,
     'char_end': 99489
    }
   },
   {
    'text': '壬戌',
    'locator': {
     'char_start': 99490,
     'char_end': 99492
    }
   },
   {
    'text': '甲辰',
    'locator': {
     'char_start': 99493,
     'char_end': 99495
    }
   },
   {
    'text': '己巳癸亥',
    'locator': {
     'char_start': 99496,
     'char_end': 99500
    }
   },
   {
    'text': '甲子',
    'locator': {
     'char_start': 99501,
     'char_end': 99503
    }
   },
   {
    'text': '乙丑',
    'locator': {
     'char_start': 99504,
     'char_end': 99506
    }
   },
   {
    'text': '丙寅',
    'locator': {
     'char_start': 99507,
     'char_end': 99509
    }
   },
   {
    'text': '丁卯',
    'locator': {
     'char_start': 99510,
     'char_end': 99512
    }
   },
   {
    'text': '戊辰',
    'locator': {
     'char_start': 99513,
     'char_end': 99515
    }
   }
  ],
  'commentary_quote_id': 'hx.example2_commentary',
  'note': '甲己化土例造二（断语自述甲木季秋、化气有余）：逐行干支 9 行组（第 4 行并书两组干支）＋断语段 [99516,99601)；逐行干支为快照版式原样逐字登记，柱位/运柱的版式读法不断言（见 limitations），断语自述的柱位指称只作原文登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.filler_2',
  'layer': '空白填充',
  'locator': {
   'char_start': 99602,
   'char_end': 99610
  },
  'note': '例造间/章末的空白填充行（单空格＋换行，快照版式原样）：无文本内容，只为使分段平铺整章、逐字可复核而登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.example_3',
  'layer': '任氏曰（例造）',
  'locator': {
   'char_start': 99610,
   'char_end': 99722
  },
  'chart_lines': [
   {
    'text': '己卯',
    'locator': {
     'char_start': 99610,
     'char_end': 99612
    }
   },
   {
    'text': '丁卯',
    'locator': {
     'char_start': 99613,
     'char_end': 99615
    }
   },
   {
    'text': '壬午',
    'locator': {
     'char_start': 99616,
     'char_end': 99618
    }
   },
   {
    'text': '甲辰丙寅',
    'locator': {
     'char_start': 99619,
     'char_end': 99623
    }
   },
   {
    'text': '乙丑',
    'locator': {
     'char_start': 99624,
     'char_end': 99626
    }
   },
   {
    'text': '甲子',
    'locator': {
     'char_start': 99627,
     'char_end': 99629
    }
   },
   {
    'text': '癸亥',
    'locator': {
     'char_start': 99630,
     'char_end': 99632
    }
   },
   {
    'text': '壬戌',
    'locator': {
     'char_start': 99633,
     'char_end': 99635
    }
   },
   {
    'text': '辛酉',
    'locator': {
     'char_start': 99636,
     'char_end': 99638
    }
   }
  ],
  'commentary_quote_id': 'hx.example3_commentary',
  'note': '丁壬化木例造三（断语自述壬水仲春、化象斯真）：逐行干支 9 行组（第 4 行并书两组干支）＋断语段 [99639,99721)；逐行干支为快照版式原样逐字登记，柱位/运柱的版式读法不断言（见 limitations），断语自述的柱位指称只作原文登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.filler_3',
  'layer': '空白填充',
  'locator': {
   'char_start': 99722,
   'char_end': 99730
  },
  'note': '例造间/章末的空白填充行（单空格＋换行，快照版式原样）：无文本内容，只为使分段平铺整章、逐字可复核而登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.example_4',
  'layer': '任氏曰（例造）',
  'locator': {
   'char_start': 99730,
   'char_end': 99835
  },
  'chart_lines': [
   {
    'text': '己卯',
    'locator': {
     'char_start': 99730,
     'char_end': 99732
    }
   },
   {
    'text': '丁卯',
    'locator': {
     'char_start': 99733,
     'char_end': 99735
    }
   },
   {
    'text': '壬午',
    'locator': {
     'char_start': 99736,
     'char_end': 99738
    }
   },
   {
    'text': '癸卯丙寅',
    'locator': {
     'char_start': 99739,
     'char_end': 99743
    }
   },
   {
    'text': '乙丑',
    'locator': {
     'char_start': 99744,
     'char_end': 99746
    }
   },
   {
    'text': '甲子',
    'locator': {
     'char_start': 99747,
     'char_end': 99749
    }
   },
   {
    'text': '癸亥',
    'locator': {
     'char_start': 99750,
     'char_end': 99752
    }
   },
   {
    'text': '壬戌',
    'locator': {
     'char_start': 99753,
     'char_end': 99755
    }
   },
   {
    'text': '辛酉',
    'locator': {
     'char_start': 99756,
     'char_end': 99758
    }
   }
  ],
  'commentary_quote_id': 'hx.example4_commentary',
  'note': '丁壬化木例造四（与前造只换一卯字，断语自述）：逐行干支 9 行组（第 4 行并书两组干支）＋断语段 [99759,99834)；逐行干支为快照版式原样逐字登记，柱位/运柱的版式读法不断言（见 limitations），断语自述的柱位指称只作原文登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.filler_4',
  'layer': '空白填充',
  'locator': {
   'char_start': 99835,
   'char_end': 99843
  },
  'note': '例造间/章末的空白填充行（单空格＋换行，快照版式原样）：无文本内容，只为使分段平铺整章、逐字可复核而登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.example_5',
  'layer': '任氏曰（例造）',
  'locator': {
   'char_start': 99843,
   'char_end': 99936
  },
  'chart_lines': [
   {
    'text': '丙戌',
    'locator': {
     'char_start': 99843,
     'char_end': 99845
    }
   },
   {
    'text': '戊戌',
    'locator': {
     'char_start': 99846,
     'char_end': 99848
    }
   },
   {
    'text': '癸巳',
    'locator': {
     'char_start': 99849,
     'char_end': 99851
    }
   },
   {
    'text': '壬戌己亥',
    'locator': {
     'char_start': 99852,
     'char_end': 99856
    }
   },
   {
    'text': '庚子',
    'locator': {
     'char_start': 99857,
     'char_end': 99859
    }
   },
   {
    'text': '辛丑',
    'locator': {
     'char_start': 99860,
     'char_end': 99862
    }
   },
   {
    'text': '壬寅',
    'locator': {
     'char_start': 99863,
     'char_end': 99865
    }
   },
   {
    'text': '癸卯',
    'locator': {
     'char_start': 99866,
     'char_end': 99868
    }
   },
   {
    'text': '甲辰',
    'locator': {
     'char_start': 99869,
     'char_end': 99871
    }
   }
  ],
  'commentary_quote_id': 'hx.example5_commentary',
  'note': '戊癸化火例造五（断语自述癸水季秋、化火斯真）：逐行干支 9 行组（第 4 行并书两组干支）＋断语段 [99872,99935)；逐行干支为快照版式原样逐字登记，柱位/运柱的版式读法不断言（见 limitations），断语自述的柱位指称只作原文登记。'
 },
 {
  'segment_id': 'ditiansui.huaxiang.tail_filler',
  'layer': '空白填充',
  'locator': {
   'char_start': 99936,
   'char_end': 99943
  },
  'note': '例造间/章末的空白填充行（单空格＋换行，快照版式原样）：无文本内容，只为使分段平铺整章、逐字可复核而登记。'
 }
]

HUAXIANG_QUOTES = [
 {
  'id': 'hx.head_verse',
  'segment_id': 'ditiansui.huaxiang.head',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '章题句',
  'role': 'chapter_head',
  'quote': '化得真者只论化,化神还有几般话。',
  'locator': {
   'char_start': 98303,
   'char_end': 98319
  },
  'condition_elements': [],
  'note': '化象章题句（化得真者只论化，化神还有几般话）：审计条目 P05 的锚点引文，本批登记后 P05 自审计条目落实为逐字登记引文。章旨陈述：真化只论化、化神另有喜忌话——非条件句本身。'
 },
 {
  'id': 'hx.yuanzhu_jiaji_cond',
  'segment_id': 'ditiansui.huaxiang.yuanzhu',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '原注',
  'role': 'formation_condition_jiaji',
  'quote': '如甲日主生于四季,单遇一位已土,在月时上合遇壬、癸、甲、乙、戊,而有一辰字,乃为化得真。',
  'locator': {
   'char_start': 98323,
   'char_end': 98367
  },
  'condition_elements': [
   'subject',
   'month_condition',
   'hour_condition',
   'multiplicity',
   'chen_factor'
  ],
  'note': '原注甲己例：甲日主生于四季（辰戌丑未）、单遇一位己土、配合在月时上合、有一辰字，乃为化得真——F5 的逐对条件原型（季节月＋独合＋辰字）。「已土」为己之形近讹字（hx-glyph-01）；「在月时上合遇壬、癸、甲、乙、戊」一段语义未决（hx-glyph-04），不作要素消费。',
  'glyph_refs': [
   'hx-glyph-01',
   'hx-glyph-04'
  ]
 },
 {
  'id': 'hx.yuanzhu_four_pairs_cond',
  'segment_id': 'ditiansui.huaxiang.yuanzhu',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '原注',
  'role': 'formation_condition_four_pairs',
  'quote': '又如丙辛生于冬月,戊癸生于夏月,乙庚生于秋月,丁壬生于春月,独自相合,又得龙以运之,此为真化矣。',
  'locator': {
   'char_start': 98367,
   'char_end': 98415
  },
  'condition_elements': [
   'subject',
   'month_condition',
   'multiplicity',
   'chen_factor',
   'wangqi'
  ],
  'note': '原注四对通则：丙辛冬、戊癸夏、乙庚秋、丁壬春，独自相合，又得龙以运之，此为真化矣——季节月即旺地的列举（同三命 F1 型）；「得龙以运之」即 E0270 C5 所记逢龙说在原注层的出处。'
 },
 {
  'id': 'hx.yuanzhu_huashen_frame',
  'segment_id': 'ditiansui.huaxiang.yuanzhu',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '原注',
  'role': 'huashen_xiji_jiaji',
  'quote': '既化矣,又论化神。如甲己化土,土阴寒,要火气昌旺;土太旺,又要取水为财,木为官,金为食神 。',
  'locator': {
   'char_start': 98415,
   'char_end': 98461
  },
  'condition_elements': [
   'huashen_xiji',
   'result_element'
  ],
  'note': '原注化神喜忌（甲己例）：既化矣又论化神——甲己化土，土阴寒要火气昌旺；土太旺又取水为财、木为官、金为食神。属化后作用面，非化之成立条件。「金为食神 」句末空格为快照版式原样（hx-glyph-03）。',
  'glyph_refs': [
   'hx-glyph-03'
  ]
 },
 {
  'id': 'hx.yuanzhu_zhengdu',
  'segment_id': 'ditiansui.huaxiang.yuanzhu',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '原注',
  'role': 'zhengdu_immunity_after_formation',
  'quote': '随其所向,论其喜忌,再见甲乙,亦不作争合妒合论。盖真化矣,如烈女不更二夫,岁运遇之皆闲神也。',
  'locator': {
   'char_start': 98461,
   'char_end': 98507
  },
  'condition_elements': [],
  'note': '原注真化后争妒不论：随其所向论其喜忌，再见甲乙亦不作争合妒合论；盖真化矣，如烈女不更二夫，岁运遇之皆闲神也。争妒只对未真化者有意义，是 F5 对阻字机制的否定形表述（与任氏曰谬论说同旨）。'
 },
 {
  'id': 'hx.renshi_origin',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'origin_theory',
  'quote': '合化之原,昔黄帝礼天于圜邱,天降十干,爱命大挠作十二支以配之。故日干曰天干,其所由,合即天一、地二、天三、地四、天五、地六、天七、地八、天九、地十之义。依数推之,则甲一、乙二、丙三、丁四、戊五、己六、庚七、辛八、壬九、癸十也。',
  'locator': {
   'char_start': 98512,
   'char_end': 98625
  },
  'condition_elements': [
   'subject'
  ],
  'note': '任氏曰合化之原：黄帝礼天圜邱、天降十干、命大挠作十二支；干合之义出于天一至地十之数合（甲一至癸十）。源说陈述，非条件句。「爱命大挠」之「爱」为疑讹（hx-glyph-02）。',
  'glyph_refs': [
   'hx-glyph-02'
  ]
 },
 {
  'id': 'hx.renshi_luoshu_pairs',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'pair_roster_by_number',
  'quote': '如“洛书”以五居中,一得五为六,故甲与己合;二得五为七,故乙与庚合;三得五为八,故丙与辛合;四得五为九,故丁与壬合;五得五为十,故戊与癸合。',
  'locator': {
   'char_start': 98625,
   'char_end': 98695
  },
  'condition_elements': [
   'result_element'
  ],
  'note': '任氏曰洛书五居中推五合：一得五为六甲己、二得五为七乙庚、三得五为八丙辛、四得五为九丁壬、五得五为十戊癸——五合名册的数理源说明，与三命 F1–F4 的名册（甲己土/乙庚金/丙辛水/丁壬木/戊癸火）一致。'
 },
 {
  'id': 'hx.renshi_fengwu',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'formation_condition_fengwu',
  'quote': '合则化,化亦必得五土而后成,五土者辰也。辰土居春,时在三阳,生物之体,气辟而动,动则变,变则化矣。且十干之合,而至五辰之位,则化气之元神发露。故甲己起甲子,至五位逢戊辰而化土;乙庚到丙子,至五位逢庚辰而化金;丙辛起戊子,至五位逢壬辰而化水;丁壬起庚子,至五位逢甲辰而化木;戊癸起壬子,至五位逢丙辰而化火。',
  'locator': {
   'char_start': 98695,
   'char_end': 98847
  },
  'condition_elements': [
   'chen_factor',
   'result_element'
  ],
  'note': '任氏曰逢五而化：合则化，化亦必得五土（辰）而后成；十干之合至五辰之位则化气元神发露——逐对逢辰干支：甲己戊辰化土、乙庚庚辰化金、丙辛壬辰化水、丁壬甲辰化木、戊癸丙辰化火。F6 的核心条件表述（辰位而非月集）。'
 },
 {
  'id': 'hx.renshi_fenglong_critique',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'fenglong_critique',
  'quote': '此相合相化之真源,近世得传者少,只知逢龙而化,不知逢五而化,辰龙之说,供引之意,如果辰为真龙。则辰年生人为龙,可行雨,而寅年生人为虎,必伤人矣。',
  'locator': {
   'char_start': 98847,
   'char_end': 98919
  },
  'condition_elements': [
   'chen_factor'
  ],
  'note': '任氏曰逢龙批判：近世只知逢龙而化、不知逢五而化；若辰为真龙，则辰年生人可行雨、寅年生人必伤人——以归谬斥辰字在场说。与原注「得龙以运之」同章并存，即 E0270 C5 登记的章内张力；本批只登记两说原文，不裁定（C5 结论不变，重审另批）。「辰龙之说，供引之意」文气不顺（hx-glyph-05）。',
  'glyph_refs': [
   'hx-glyph-05'
  ]
 },
 {
  'id': 'hx.renshi_xiji_frame',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'huashen_xiji_frame',
  'quote': '至于化象作用,亦有喜忌配合之理,所以“化神还有几般话”也。非化斯神,喜见斯神,执一而论也,是化象亦要究其衰旺,审其虚实,察其喜忌,则吉凶有验,否泰了然矣。',
  'locator': {
   'char_start': 98919,
   'char_end': 98996
  },
  'condition_elements': [
   'huashen_xiji'
  ],
  'note': '任氏曰化象作用总纲：化象亦要究其衰旺、审其虚实、察其喜忌——化神喜忌以化神自身的衰旺虚实为据（化后作用面）；其中衰旺指化神之衰旺，不是日主一般旺衰判据，不作旺衰要素消费。'
 },
 {
  'id': 'hx.renshi_yushe_yubu',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'huashen_xiji_rule',
  'quote': '如化神旺而有余,宜泄化神之神为用;化神衰而不足,宜生助化神之神为用。',
  'locator': {
   'char_start': 98996,
   'char_end': 99030
  },
  'condition_elements': [
   'huashen_xiji'
  ],
  'note': '任氏曰化神喜忌通则：化神旺而有余宜泄化神之神为用，衰而不足宜生助化神之神为用——取用方向陈述（化后），非化之成立条件，非扶抑通则，不作任何用神裁定。'
 },
 {
  'id': 'hx.renshi_yushe_example',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'huashen_xiji_worked_example_yushe',
  'quote': '如甲己化土,生于未戌月,土燥而旺,干透丙丁,支藏巳午。谓之有余,再行火土之运,必太过而不吉也。须从其意向,柱中有水,要行金运;柱中有金,要行水运;无金无水,土势太旺,秘要金泄之;火土过燥,要带水之金运以润之。',
  'locator': {
   'char_start': 99030,
   'char_end': 99134
  },
  'condition_elements': [
   'huashen_xiji'
  ],
  'note': '任氏曰甲己化土有余例：生于未戌月土燥而旺，谓之有余，再行火土之运必太过；须从其意向（柱中有水行金运、有金行水运、无金无水秘要金泄、火土过燥带水之金运）。例说陈述，非通则。「秘要金泄之」之「秘」语义存疑（hx-glyph-06）。',
  'glyph_refs': [
   'hx-glyph-06'
  ]
 },
 {
  'id': 'hx.renshi_buzu_example',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'huashen_xiji_worked_example_buzu',
  'quote': '生于丑辰月,土湿为弱,火虽有虚,水木无而实,或干支杂其金水,谓之不足,亦须从其意向。柱中有金,要行火运;柱中有水,要行土运;金水并见,过于虚湿,要带火之土运以实之,助起化神为吉也。',
  'locator': {
   'char_start': 99134,
   'char_end': 99224
  },
  'condition_elements': [
   'huashen_xiji'
  ],
  'note': '任氏曰甲己化土不足例：生于丑辰月土湿为弱，谓之不足，亦须从其意向（柱中有金行火运、有水行土运、金水并见带火之土运助起化神）。例说陈述，非通则。「火虽有虚，水木无而实」文气不顺（hx-glyph-07）。',
  'glyph_refs': [
   'hx-glyph-07'
  ]
 },
 {
  'id': 'hx.renshi_zhengdu',
  'segment_id': 'ditiansui.huaxiang.renshi',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰',
  'role': 'zhengdu_denial',
  'quote': '至于争合妒合之说,乃谬论也,既合而化,如贞妇配义夫,从一而终,不生二心,见戊己是彼之同类,遇甲乙是我之本气,有相让之谊。合而不化,勉强之意,必非佳偶。见戊己多而起争妒之风,遇甲乙众而更强弱之性。甲己之合如此,余可类推。',
  'locator': {
   'char_start': 99224,
   'char_end': 99333
  },
  'condition_elements': [],
  'note': '任氏曰争合妒合谬论：既合而化如贞妇配义夫，从一而终不生二心（见戊己是同类、遇甲乙是本气，有相让之谊）；合而不化，勉强之意，见戊己多而起争妒之风、遇甲乙众而更强弱之性——争妒被任氏定位为合而不化的现象而非真化的阻字机制，与三命 F1 妬合/ F3 妬化字集是同题异述，本批不并入其冲突结构。'
 },
 {
  'id': 'hx.example1_commentary',
  'segment_id': 'ditiansui.huaxiang.example_1',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰（例造）',
  'role': 'worked_example_commentary',
  'quote': '年月两干之甲乙,得当令之申金、丑内之辛金制化,不起争妒之风。时干己土临旺,与日主亲切而合,合神真实,乃谓真化。但秋金当令,化神泄气不足。至午运助化神,中乡榜;辛巳金火土并旺,癸黄甲,宴琼林,入翰苑,仕黄堂,庚辰合乙制化比劫,仕至藩臬。',
  'locator': {
   'char_start': 99363,
   'char_end': 99480
  },
  'condition_elements': [],
  'note': '例造断语（甲己化土例造一（断语自述年月两干甲乙、时干己土、真化））：任氏对本例造的真化/化神有余不足与行运仕途陈述——例造见证，非规则；仕途吉凶断语只登记存在、不作裁定，不据例造反推条件。「癸黄甲」「仕黄堂」之「黄」语义存疑（hx-glyph-08/09）。',
  'glyph_refs': [
   'hx-glyph-08',
   'hx-glyph-09'
  ]
 },
 {
  'id': 'hx.example2_commentary',
  'segment_id': 'ditiansui.huaxiang.example_2',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰（例造）',
  'role': 'worked_example_commentary',
  'quote': '甲木生于季秋,土旺乘权,克去壬水,又无比劫,合神更真,化气有余。惜运走东北水木之地,功名仕路,不及前造,至丑运丁酉年,暗会金局,泄化神而吐秀,登科;戊戌年发甲,仕至州牧。',
  'locator': {
   'char_start': 99516,
   'char_end': 99601
  },
  'condition_elements': [],
  'note': '例造断语（甲己化土例造二（断语自述甲木季秋、化气有余））：任氏对本例造的真化/化神有余不足与行运仕途陈述——例造见证，非规则；仕途吉凶断语只登记存在、不作裁定，不据例造反推条件。'
 },
 {
  'id': 'hx.example3_commentary',
  'segment_id': 'ditiansui.huaxiang.example_3',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰（例造）',
  'role': 'worked_example_commentary',
  'quote': '壬水生于仲春,化象斯真。最喜甲木元神透露,化气有余。余则宜泄,斯化神吐秀,喜其坐下午,午生辰土,秀气流行。少年科甲,翰苑名高,惜乎中运水旺之地,未能显秩,终于县宰。',
  'locator': {
   'char_start': 99639,
   'char_end': 99721
  },
  'condition_elements': [],
  'note': '例造断语（丁壬化木例造三（断语自述壬水仲春、化象斯真））：任氏对本例造的真化/化神有余不足与行运仕途陈述——例造见证，非规则；仕途吉凶断语只登记存在、不作裁定，不据例造反推条件。'
 },
 {
  'id': 'hx.example4_commentary',
  'segment_id': 'ditiansui.huaxiang.example_4',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰（例造）',
  'role': 'worked_example_commentary',
  'quote': '此与前造只换一卯字,化象更真,化神更有余。嫌其癸劫争财,年干己土,透隔无根,不能去其癸水。午火未能流行。此癸水,真乃夺标之客也。虽中乡榜,终不能出仕。',
  'locator': {
   'char_start': 99759,
   'char_end': 99834
  },
  'condition_elements': [],
  'note': '例造断语（丁壬化木例造四（与前造只换一卯字，断语自述））：任氏对本例造的真化/化神有余不足与行运仕途陈述——例造见证，非规则；仕途吉凶断语只登记存在、不作裁定，不据例造反推条件。'
 },
 {
  'id': 'hx.example5_commentary',
  'segment_id': 'ditiansui.huaxiang.example_5',
  'source_id': 'bazi.source.ditiansui-spouse',
  'layer': '任氏曰（例造）',
  'role': 'worked_example_commentary',
  'quote': '癸水生于季秋,丙火透而通根,化火斯真。嫌其时透壬水克丙,只中乡榜,直至卯运,壬水绝地,挑知县,历三任而不升,亦壬水夺财之故也。',
  'locator': {
   'char_start': 99872,
   'char_end': 99935
  },
  'condition_elements': [],
  'note': '例造断语（戊癸化火例造五（断语自述癸水季秋、化火斯真））：任氏对本例造的真化/化神有余不足与行运仕途陈述——例造见证，非规则；仕途吉凶断语只登记存在、不作裁定，不据例造反推条件。「挑知县」之「挑」语义存疑（hx-glyph-10）。',
  'glyph_refs': [
   'hx-glyph-10'
  ]
 }
]

HUAXIANG_CONDITION_STRUCTURE = {
 'scope_note': '两套条件表述的要素构成只做结构登记：要素词汇沿 E0270 合化审定的 11 要素（subject/month_condition/hour_condition/third_stem_blocker/multiplicity/wangqi/root_qi/commander/chen_factor/strength_polarity/result_element），另加两层共有的化后作用面 huashen_xiji（E0270 矩阵为成立条件面、无此行；本批不并入其矩阵）。每项要素附本批登记引文为据；adjudication 恒 None。',
 'formulations': [
  {
   'id': 'F5',
   'name': '滴天髓化象原注真化条件',
   'layer': '原注',
   'register_ref_before': 'docs/product/BAZI_PATTERN_AUDIT.md P05（审计条目）；E0270 登记册 F5（audit_entry_only_not_registered）',
   'registered_in_this_batch': True,
   'adjudication': None,
   'status': 'registered_unadjudicated',
   'elements': {
    'subject': {
     'text': '日主（日干与合神）',
     'evidence': [
      'hx.yuanzhu_jiaji_cond',
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'month_condition': {
     'text': '季节月：甲己四季（辰戌丑未）/丙辛冬/戊癸夏/乙庚秋/丁壬春',
     'evidence': [
      'hx.yuanzhu_jiaji_cond',
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'hour_condition': {
     'text': '仅甲己例：配合之神在月时上合',
     'evidence': [
      'hx.yuanzhu_jiaji_cond'
     ]
    },
    'third_stem_blocker': {
     'text': '未决：甲己例「在月时上合遇壬、癸、甲、乙、戊」字样语义未决（疑有讹乱，hx-glyph-04），不作要素消费；原注另以真化后不作争合妒合论否定阻字机制对真化的适用',
     'evidence': [
      'hx.yuanzhu_jiaji_cond',
      'hx.yuanzhu_zhengdu'
     ],
     'glyph_refs': [
      'hx-glyph-04'
     ]
    },
    'multiplicity': {
     'text': '独自相合/单遇一位（独合）',
     'evidence': [
      'hx.yuanzhu_jiaji_cond',
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'wangqi': {
     'text': '以季节月列举旺地（同三命 F1 型），无独立旺气判据',
     'evidence': [
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'root_qi': {
     'text': 'absent（辰字另列 chen_factor）',
     'evidence': []
    },
    'commander': {
     'text': 'absent（不用分日司令，与 E0270 命题 P14 一致）',
     'evidence': []
    },
    'chen_factor': {
     'text': '甲己例：有一辰字；通则：得龙以运之（逢龙而化）',
     'evidence': [
      'hx.yuanzhu_jiaji_cond',
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'strength_polarity': {
     'text': '真化（与假化对举，章内只展开真化条件）',
     'evidence': [
      'hx.head_verse',
      'hx.yuanzhu_jiaji_cond',
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'result_element': {
     'text': '名册固定（甲己土/乙庚金/丙辛水/丁壬木/戊癸火）',
     'evidence': [
      'hx.yuanzhu_huashen_frame',
      'hx.yuanzhu_four_pairs_cond'
     ]
    },
    'huashen_xiji': {
     'text': '既化矣又论化神：随其所向论其喜忌（甲己化土例：土阴寒要火气昌旺、太旺取水为财/木为官/金为食神）；真化后再见甲乙不作争合妒合论',
     'evidence': [
      'hx.yuanzhu_huashen_frame',
      'hx.yuanzhu_zhengdu'
     ]
    }
   }
  },
  {
   'id': 'F6',
   'name': '滴天髓化象任氏曰真化条件（合则化/逢五而化）',
   'layer': '任氏曰',
   'register_ref_before': '同 F5（任氏曰层，审计条目）；E0270 登记册 F6（audit_entry_only_not_registered）',
   'registered_in_this_batch': True,
   'adjudication': None,
   'status': 'registered_unadjudicated',
   'elements': {
    'subject': {
     'text': '日干（合则化之源说）',
     'evidence': [
      'hx.renshi_origin',
      'hx.renshi_fengwu'
     ]
    },
    'month_condition': {
     'text': 'absent（以辰位立论，非月集）',
     'evidence': []
    },
    'hour_condition': {
     'text': 'absent',
     'evidence': []
    },
    'third_stem_blocker': {
     'text': '否定形：争合妒合之说乃谬论——既合而化不生争妒，争妒只起于合而不化；无阻字字集',
     'evidence': [
      'hx.renshi_zhengdu'
     ]
    },
    'multiplicity': {
     'text': 'absent',
     'evidence': []
    },
    'wangqi': {
     'text': 'absent（化神衰旺属化后喜忌面，另列 huashen_xiji）',
     'evidence': []
    },
    'root_qi': {
     'text': 'absent',
     'evidence': []
    },
    'commander': {
     'text': 'absent（与 E0270 命题 P14 一致）',
     'evidence': []
    },
    'chen_factor': {
     'text': '化必得五土（辰）而后成、逢五而化：十干之合至五辰之位，逐对逢辰干支（甲己戊辰/乙庚庚辰/丙辛壬辰/丁壬甲辰/戊癸丙辰）；并斥逢龙说（只知逢龙而化，不知逢五而化）',
     'evidence': [
      'hx.renshi_fengwu',
      'hx.renshi_fenglong_critique'
     ]
    },
    'strength_polarity': {
     'text': 'absent',
     'evidence': []
    },
    'result_element': {
     'text': '名册固定（同 F5；逢辰列举逐对给出化元素）',
     'evidence': [
      'hx.renshi_luoshu_pairs',
      'hx.renshi_fengwu'
     ]
    },
    'huashen_xiji': {
     'text': '化象亦要究其衰旺、审其虚实、察其喜忌：化神旺而有余宜泄化神之神为用，衰而不足宜生助化神之神为用（甲己化土未戌月有余/丑辰月不足两例展开）',
     'evidence': [
      'hx.renshi_xiji_frame',
      'hx.renshi_yushe_yubu',
      'hx.renshi_yushe_example',
      'hx.renshi_buzu_example'
     ]
    }
   }
  }
 ],
 'relation_to_sanming_f1_f4': 'same_topic_different_statements',
 'merged_into_hehua_conflict_structure': False
}

HUAXIANG_RELATIONS = [
 {
  'id': 'hx-rel-01',
  'with': '三命卷二合化组四表述 F1–F4（018-C 登记、E0270 审定）',
  'relation': 'same_topic_different_statements',
  'note': '同题异述事实登记：滴天髓原注/任氏曰与三命四表述同论天干五合化气条件，要素构成各异（F5 季节月＋独合＋逢龙、F6 辰位逢五；F1 逐对月集、F2 旺气、F3 有二则化、F4 逐月表）。本批不做冲突裁定、不并入 E0270 冲突结构：C1–C4 的表述集合与结论不变，本登记不新增冲突项。',
  'e0270_conclusions_changed': False
 },
 {
  'id': 'hx-rel-02',
  'with': 'E0270 CONFLICT_ANALYSIS C5（滴天髓化象章内逢龙/逢五张力）',
  'relation': 'registration_basis_now_supplied',
  'note': 'C5 在 E0270 中以审计条目为据、只记结构；本批登记后其两造原文（原注 hx.yuanzhu_four_pairs_cond「得龙以运之」与任氏曰 hx.renshi_fengwu/hx.renshi_fenglong_critique「逢五而化」）已可作引文消费。C5 的登记文本与定性本批逐字不改；是否重审属后续批次。',
  'e0270_conclusions_changed': False
 },
 {
  'id': 'hx-rel-03',
  'with': '三命卷六《化象》节从化象 doctrine（018-G 登记、E0270 登记册 HX）',
  'relation': 'different_adjudication_object',
  'note': '对象区分保持：本章章题虽作「化象」，内容为干合化气（合而化否）的条件表述；三命卷六《化象》论日主从化（从化否）。两者不是同一裁定对象——化气表述采用属待裁定 P-D1、从化象分类属待裁定 P-D2（E0270 分开登记），本批不合并、不混同，章题同名只作事实注记。',
  'e0270_conclusions_changed': False
 },
 {
  'id': 'hx-rel-04',
  'with': '审计条目 P05（docs/product/BAZI_PATTERN_AUDIT.md）',
  'relation': 'audit_entry_superseded_by_registration',
  'note': 'P05 是本章此前唯一的在案记录（锚点 98303 章题句＋「真化需要另审资格和后文；五合结构存在不等于成化」）；本批即 E0270 PENDING_ITEMS B4 预定的逐节登记批，P05 自此落实为逐字登记（登记册 bazi-ditiansui-huaxiang-registration-v1）。审计文档原文不在本批改动面。',
  'e0270_conclusions_changed': False
 }
]

HUAXIANG_GLYPH_NOTES = [
 {
  'id': 'hx-glyph-01',
  'position': 98336,
  'char': '已',
  'quote_id': 'hx.yuanzhu_jiaji_cond',
  'status': 'suspected_transcription_preserved',
  'mapped_reading': None,
  'note': '「单遇一位已土」之「已」：干名当为己（甲己合），已/己形近混用；E0270 F5 概要即以己土著录。逐字保留、无见证不径改。'
 },
 {
  'id': 'hx-glyph-02',
  'position': 98531,
  'char': '爱',
  'quote_id': 'hx.renshi_origin',
  'status': 'suspected_transcription_preserved',
  'mapped_reading': None,
  'note': '「爱命大挠作十二支」之「爱」：与「天降十干」对文，当为「爰」之讹（爰命大挠）；逐字保留、不径改。'
 },
 {
  'id': 'hx-glyph-03',
  'position': 98459,
  'char': ' ',
  'quote_id': 'hx.yuanzhu_huashen_frame',
  'status': 'typesetting_space_preserved',
  'mapped_reading': None,
  'note': '「金为食神 。」句号前一空格：快照版式空格原样保留（章内正文空格仅此一处，其余空格均为段间空白填充行）；引文逐字含此空格，不剔除、不补读。'
 },
 {
  'id': 'hx-glyph-04',
  'span': {
   'char_start': 98344,
   'char_end': 98354
  },
  'char': None,
  'quote_id': 'hx.yuanzhu_jiaji_cond',
  'status': 'suspected_text_disorder_preserved',
  'mapped_reading': None,
  'note': '「在月时上合遇壬、癸、甲、乙、戊」一段：承「单遇一位己土」之后，五干并列而谓语不明，文气不顺，疑有脱字/讹字；整段按快照原字登记，语义未决、不作 third_stem_blocker 等任何要素消费（与 E0270 矩阵 F5 该格口径一致）。'
 },
 {
  'id': 'hx-glyph-05',
  'span': {
   'char_start': 98877,
   'char_end': 98886
  },
  'char': None,
  'quote_id': 'hx.renshi_fenglong_critique',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '「辰龙之说，供引之意」：句意不顺，「供引」疑有讹字；逐字保留，批判主旨（下句归谬）不受影响，不据此句作任何读法。'
 },
 {
  'id': 'hx-glyph-06',
  'position': 99113,
  'char': '秘',
  'quote_id': 'hx.renshi_yushe_example',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '「土势太旺，秘要金泄之」之「秘」：于动词位语义存疑，疑为转写之讹；逐字保留、不径改。'
 },
 {
  'id': 'hx-glyph-07',
  'span': {
   'char_start': 99145,
   'char_end': 99155
  },
  'char': None,
  'quote_id': 'hx.renshi_buzu_example',
  'status': 'suspected_text_disorder_preserved',
  'mapped_reading': None,
  'note': '「火虽有虚，水木无而实」：与上文「土湿为弱」及有余例的对文不顺，疑有讹倒；整段按快照原字登记，不复原、不改读。'
 },
 {
  'id': 'hx-glyph-08',
  'position': 99451,
  'char': '黄',
  'quote_id': 'hx.example1_commentary',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '例造一断语「癸黄甲」之「黄」：夹在「辛巳金火土并旺」与「宴琼林」之间，语义不顺，疑为转写之讹；逐字保留。'
 },
 {
  'id': 'hx-glyph-09',
  'position': 99463,
  'char': '黄',
  'quote_id': 'hx.example1_commentary',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '例造一断语「仕黄堂」之「黄」：官署名语义存疑，疑为转写之讹；逐字保留。'
 },
 {
  'id': 'hx-glyph-10',
  'position': 99915,
  'char': '挑',
  'quote_id': 'hx.example5_commentary',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '例造五断语「挑知县」之「挑」：授官义语义存疑（疑近铨选之讹）；逐字保留、不径改。'
 }
]

HUAXIANG_NOTES = [
 'R1 登记≠可判：本批为纯证据登记，零判定代码；本章登记不产出任何从化/化气/化格判定，determination 面零变化，bazi_action_conditions 的 transformation_status 恒 unresolved 逐字不变。',
 'R2 层属分明：整章按章题句/原注/任氏曰/任氏例造四层分段登记，原注与任氏曰两套条件表述逐段分开、引文逐条标层，不混层；层属标记「原注:」「任氏曰:」的位点与半角冒号原样钉定。',
 'R3 与 E0270 的关系：本批落实其 PENDING_ITEMS B4（滴天髓化象章登记）；E0270 合化审定登记册逐字不改——其 F5/F6 的 audit_entry_only 是该册盘点时点的记录，本批登记在其自身登记字段中著录（register_ref_before），两册并存、时点分明；C1–C5、P-D1/P-D2 与 SLICE_SPEC=None 结论不变。',
 'R4 同题异述：F5/F6 与三命 F1–F4 的关系只登记同题异述事实，不做冲突裁定、不并入合化 conflict 结论、不新增冲突项；章内逢龙/逢五张力（C5）的重审以本登记为前提、属后续批次，本批不预判。',
 'R5 对象区分：本章题名「化象」而内容为干合化气条件；与三命卷六《化象》从化象 doctrine 不是同一裁定对象（P-D1/P-D2 分开登记在案），下游不得把任一方的条件错接到另一对象。',
 'R6 疑讹纪律：章内字形/语义疑点 10 项逐项落账（hx-glyph-01..10），逐字保留快照原字，mapped_reading 一律为 None——无他本互校者不给校定读法、不径改；章内半角 ? 0 处、PUA 0 处（全书 ? 共 132 处均在章外，不在本批范围）。',
 'R7 来源普查不变：滴天髓 Source 仍为既有 101 条之一（C 95 / D 6），本批只扩其 review_scope，不新增 Source、不升证据等级；本登记为公开仓证据登记，Canonical/Phase1 正式注册 pending（与既有研究级登记同口径披露），不借用 s 编号。'
]

HUAXIANG_LIMITATIONS = [
 '化气成立仍不可判：四表述（含本批新登记的 F5/F6）采用属用户级待裁定 P-D1，本批未呈请、未代裁；从化象分类属 P-D2，同样未裁。登记齐备不等于可执行。',
 '例造版式读法未断言：五例造的逐行干支（9 行组、第 4 行并书两组）只作快照版式原样登记；纯文本快照无版式标记，年/月/日/时与运柱的对应关系不断言、不据例造重构命盘、不产出例造 Golden（断语自述的柱位指称只作原文登记）。',
 '原注甲己例「在月时上合遇壬、癸、甲、乙、戊」语义未决（hx-glyph-04）：该句在缺字/讹字解决前不作任何要素消费；本批未做任何他本互校。',
 '渊海/神峰/穷通快照中的化气/化象字样仍未登记（E0270 盘点缺口原样保留），不在本批范围；滴天髓其余诸章亦不在本批范围。',
 '化神喜忌（huashen_xiji）只作结构登记：其取用方向陈述以化神衰旺为据，与扶抑（日主旺衰方向表）是不同对象，不作扶抑/用神消费，不解锁 TJ-013.1。'
]

HUAXIANG_REGISTRATION_STATUS = {
 'research_only': True,
 'public_enabled': False,
 'ai_enabled': False,
 'canonical_phase1_registration': 'pending',
 'determination_surface_changed': False,
 'transformation_status': 'unresolved',
 'hehua_register_changed': False,
 'source_census': '101 (C 95 / D 6) unchanged',
 'pending_items_unlocked': [
  'E0270 PENDING_ITEMS B4 (registration)'
 ],
 'pending_decisions_unchanged': [
  'P-D1',
  'P-D2'
 ]
}
