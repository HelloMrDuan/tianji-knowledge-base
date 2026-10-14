/**
 * TJ-008.7 首页深青夜景（第二轮）：「楼阁露台凭栏观月」构图。
 * 以 docs/product/designs/night-ink/approved-reference.webp 左上「首页·桌面端」为基准：
 * 木构楼阁（檐角/窗棂/暖光）、大灯笼、书卷、梅枝前景，远山薄雾、湖面月影、湖岸灯火。
 * 水墨质感用 feTurbulence + 置换滤镜实现，非简单几何堆砌。
 * 桌面 / 手机各一套独立构图（手机不再是宽幅 slice 裁切）。
 * 纯装饰：aria-hidden；动画仅氛围点缀，prefers-reduced-motion 下静态。
 */

function Blossom({ x, y, s = 1 }: { x: number; y: number; s?: number }) {
  const petals = [0, 72, 144, 216, 288];
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity="0.94">
      {petals.map((a) => (
        <ellipse
          key={a}
          cx="0"
          cy="-5.2"
          rx="3.4"
          ry="5.6"
          fill="#d78a9b"
          opacity="0.88"
          transform={`rotate(${a})`}
        />
      ))}
      <circle r="1.9" fill="#8e2f42" />
    </g>
  );
}

function Bud({ x, y, s = 1 }: { x: number; y: number; s?: number }) {
  return <circle cx={x} cy={y} r={2.6 * s} fill="#c96a7e" opacity="0.9" />;
}

const STARS_D: Array<[number, number, number, number]> = [
  [80, 60, 1.6, 0.7], [210, 140, 1.2, 0.5], [340, 70, 1.8, 0.8], [470, 150, 1.1, 0.4],
  [590, 60, 1.5, 0.65], [700, 130, 1.2, 0.5], [820, 50, 1.7, 0.75], [940, 160, 1.1, 0.45],
  [1030, 60, 1.4, 0.6], [1290, 220, 1.3, 0.55], [1380, 90, 1.6, 0.7], [150, 240, 1.2, 0.45],
  [520, 230, 1.4, 0.55], [760, 210, 1.1, 0.4], [80, 330, 1.3, 0.5], [620, 260, 1.2, 0.45],
  [880, 250, 1.5, 0.6], [1080, 280, 1.1, 0.4], [1240, 300, 1.4, 0.55], [420, 300, 1.2, 0.45],
  [260, 200, 1.3, 0.5], [1330, 180, 1.2, 0.5], [60, 180, 1.5, 0.6], [960, 90, 1.3, 0.55],
];

const SHORE_D: Array<[number, number]> = [
  [500, 442], [560, 438], [640, 444], [700, 439], [780, 443], [850, 438],
  [920, 442], [1000, 439], [1060, 443], [1230, 440], [1300, 443], [1360, 439],
];

const BLOSSOMS_D: Array<[number, number, number]> = [
  [60, 66, 1.1], [120, 58, 0.9], [180, 72, 1.2], [240, 92, 1], [300, 108, 0.85],
  [360, 118, 1.05], [410, 108, 0.9], [150, 105, 0.8], [210, 130, 0.95],
  [280, 140, 0.85], [330, 130, 1], [90, 95, 0.75], [390, 128, 0.8],
];

function DesktopScene() {
  return (
    <svg
      className="night-hero-scene"
      viewBox="0 0 1440 640"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <linearGradient id="nhs-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0e2431" />
          <stop offset="0.55" stopColor="#0a1a23" />
          <stop offset="1" stopColor="#060f14" />
        </linearGradient>
        <radialGradient id="nhs-moon-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#f6eecf" stopOpacity="0.4" />
          <stop offset="0.55" stopColor="#f6eecf" stopOpacity="0.13" />
          <stop offset="1" stopColor="#f6eecf" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="nhs-moon" cx="0.42" cy="0.38" r="0.75">
          <stop offset="0" stopColor="#fdf6dd" />
          <stop offset="0.8" stopColor="#f2e2b4" />
          <stop offset="1" stopColor="#e3cd96" />
        </radialGradient>
        <linearGradient id="nhs-lake" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0e2733" />
          <stop offset="1" stopColor="#050d12" />
        </linearGradient>
        <linearGradient id="nhs-refl" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f2e3b0" stopOpacity="0.55" />
          <stop offset="1" stopColor="#f2e3b0" stopOpacity="0" />
        </linearGradient>
        <radialGradient id="nhs-lantern-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#f5b545" stopOpacity="0.5" />
          <stop offset="1" stopColor="#f5b545" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="nhs-lantern-body" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f8c463" />
          <stop offset="0.55" stopColor="#f0a83e" />
          <stop offset="1" stopColor="#d67f27" />
        </linearGradient>
        <linearGradient id="nhs-wood" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#2e1c12" />
          <stop offset="0.5" stopColor="#1c100a" />
          <stop offset="1" stopColor="#120a06" />
        </linearGradient>
        <radialGradient id="nhs-window" cx="0.5" cy="0.45" r="0.75">
          <stop offset="0" stopColor="#f6bd63" />
          <stop offset="0.7" stopColor="#d98a35" />
          <stop offset="1" stopColor="#a85a1c" />
        </radialGradient>
        <radialGradient id="nhs-vignette" cx="0.5" cy="0.46" r="0.85">
          <stop offset="0.55" stopColor="#04090c" stopOpacity="0" />
          <stop offset="1" stopColor="#04090c" stopOpacity="0.55" />
        </radialGradient>
        {/* 月光洗礼（右侧山水） */}
        <radialGradient id="nhs-moonwash" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#9fc3d4" stopOpacity="0.22" />
          <stop offset="1" stopColor="#9fc3d4" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="nhs-lake-shimmer" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#7fa8b8" stopOpacity="0" />
          <stop offset="0.55" stopColor="#7fa8b8" stopOpacity="0.14" />
          <stop offset="1" stopColor="#7fa8b8" stopOpacity="0" />
        </linearGradient>
        <filter id="nhs-ink" x="-8%" y="-8%" width="116%" height="116%">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.03" numOctaves="2" seed="7" result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale="20" />
        </filter>
        <filter id="nhs-ink2" x="-8%" y="-8%" width="116%" height="116%">
          <feTurbulence type="fractalNoise" baseFrequency="0.02 0.05" numOctaves="2" seed="11" result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale="12" />
        </filter>
        <filter id="nhs-soft" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="7" />
        </filter>
      </defs>

      {/* 夜空 */}
      <rect x="0" y="0" width="1440" height="640" fill="url(#nhs-sky)" />
      <g fill="#dfe9e4">
        {STARS_D.map(([x, y, r, o], i) => (
          <circle key={i} cx={x} cy={y} r={r} opacity={o} />
        ))}
      </g>

      {/* 月 */}
      <circle cx="1140" cy="118" r="118" fill="url(#nhs-moon-halo)" />
      <circle cx="1140" cy="118" r="50" fill="url(#nhs-moon)" />
      <circle cx="1124" cy="104" r="9" fill="#d9c28c" opacity="0.5" />
      <circle cx="1156" cy="132" r="6" fill="#d9c28c" opacity="0.45" />
      <circle cx="1142" cy="128" r="4" fill="#d9c28c" opacity="0.4" />

      {/* 远山（水墨置换，淡） */}
      <g filter="url(#nhs-ink)" opacity="0.9">
        <path
          d="M0,400 L90,340 L170,372 L260,318 L350,366 L450,330 L540,374 L640,336 L740,372 L840,326 L940,368 L1040,338 L1140,370 L1240,332 L1340,366 L1440,344 L1440,440 L0,440 Z"
          fill="#1e3d47"
        />
      </g>
      {/* 中山 */}
      <g filter="url(#nhs-ink2)">
        <path
          d="M0,442 L70,398 L150,430 L240,392 L330,432 L430,400 L520,436 L620,404 L720,434 L820,398 L920,432 L1020,402 L1120,434 L1220,404 L1320,432 L1440,410 L1440,470 L0,470 Z"
          fill="#12262e"
        />
      </g>

      {/* 湖 */}
      <rect x="0" y="440" width="1440" height="120" fill="url(#nhs-lake)" />
      {/* 月影 */}
      <rect x="1106" y="442" width="68" height="112" fill="url(#nhs-refl)" opacity="0.55" />
      <g stroke="#e9d9a6" strokeWidth="2.4" strokeLinecap="round">
        {[
          [448, 1140, 56, 0.34], [461, 1132, 48, 0.3], [474, 1148, 42, 0.26],
          [488, 1134, 36, 0.22], [502, 1144, 30, 0.18], [516, 1136, 25, 0.14],
          [530, 1142, 20, 0.1], [542, 1138, 16, 0.07],
        ].map(([y, cx, hw, o], i) => (
          <line key={i} x1={cx - hw} y1={y} x2={cx + hw} y2={y} opacity={o} />
        ))}
      </g>
      {/* 湖岸灯火 */}
      <g>
        {SHORE_D.map(([x, y], i) => (
          <g key={i}>
            <circle cx={x} cy={y} r="7" fill="#f0b95a" opacity="0.28" />
            <circle cx={x} cy={y} r="2.4" fill="#f6c86a" opacity="0.9" />
          </g>
        ))}
      </g>
      {/* 远岸小阁剪影（右） */}
      <g opacity="0.92">
        <rect x="1246" y="398" width="10" height="44" fill="#0c1418" />
        <rect x="1268" y="398" width="10" height="44" fill="#0c1418" />
        <rect x="1240" y="388" width="44" height="10" fill="#0c1418" />
        <path d="M1262,372 Q1274,380 1288,388 L1236,388 Q1250,380 1262,372 Z" fill="#0a1014" />
        <path d="M1232,388 Q1262,380 1292,388 L1288,394 Q1262,387 1236,394 Z" fill="#11181d" />
        <rect x="1250" y="404" width="6" height="10" fill="#e8a84c" opacity="0.85" />
        <rect x="1268" y="404" width="6" height="10" fill="#e8a84c" opacity="0.7" />
      </g>
      {/* 湖面波纹 */}
      <g stroke="#9fb6bd" strokeWidth="1.4" opacity="0.16" strokeLinecap="round">
        <line x1="180" y1="486" x2="330" y2="486" />
        <line x1="420" y1="508" x2="560" y2="508" />
        <line x1="700" y1="492" x2="860" y2="492" />
        <line x1="950" y1="520" x2="1060" y2="520" />
        <line x1="1240" y1="500" x2="1360" y2="500" />
      </g>
      {/* 月光洒湖 + 山体受光 */}
      <ellipse cx="1050" cy="470" rx="420" ry="90" fill="url(#nhs-lake-shimmer)" />
      <ellipse cx="1140" cy="330" rx="380" ry="150" fill="url(#nhs-moonwash)" />
      {/* 第二层薄雾（中景） */}
      <ellipse className="nhs-mist" cx="980" cy="400" rx="300" ry="18" fill="#dfe9e4" opacity="0.06" filter="url(#nhs-soft)" />

      {/* 薄雾 */}
      <ellipse className="nhs-mist nhs-mist-1" cx="680" cy="428" rx="480" ry="24" fill="#dfe9e4" opacity="0.07" filter="url(#nhs-soft)" />
      <ellipse className="nhs-mist nhs-mist-2" cx="380" cy="516" rx="360" ry="20" fill="#dfe9e4" opacity="0.05" filter="url(#nhs-soft)" />

      {/* 近岸暗影 */}
      <g filter="url(#nhs-ink2)">
        <path d="M0,560 L120,528 L280,548 L420,532 L600,552 L780,534 L960,550 L1140,536 L1300,552 L1440,540 L1440,600 L0,600 Z" fill="#0a151b" />
      </g>

      {/* ============ 楼阁（左） ============ */}
      <g>
        {/* 台基 */}
        <rect x="44" y="548" width="336" height="22" fill="#1c130d" />
        <rect x="44" y="548" width="336" height="4" fill="#3d2c1e" opacity="0.9" />
        {/* 柱 */}
        {[84, 196, 308].map((x) => (
          <g key={x}>
            <rect x={x} y="402" width="18" height="146" fill="url(#nhs-wood)" />
            <rect x={x} y="402" width="4" height="146" fill="#5a4028" opacity="0.35" />
            <rect x={x - 5} y="540" width="28" height="10" fill="#0f0a07" />
          </g>
        ))}
        {/* 阑额（横梁） */}
        <rect x="64" y="384" width="312" height="20" fill="#241610" />
        <rect x="64" y="384" width="312" height="3" fill="#4a3320" opacity="0.7" />
        {/* 斗拱（简化） */}
        {[84, 196, 308].map((x) => (
          <g key={x} fill="#2e1c10">
            <rect x={x - 9} y="370" width="36" height="14" rx="2" />
            <rect x={x - 4} y="362" width="26" height="10" rx="2" />
          </g>
        ))}
        {/* 发光窗棂 ×2 */}
        {[108, 220].map((x) => (
          <g key={x}>
            <rect x={x} y="414" width="72" height="120" fill="url(#nhs-window)" opacity="0.95" />
            <rect x={x} y="414" width="72" height="120" fill="none" stroke="#180d07" strokeWidth="7" />
            <g stroke="#2a170e" strokeWidth="2.6" opacity="0.9">
              {[x + 18, x + 36, x + 54].map((vx) => (
                <line key={vx} x1={vx} y1="414" x2={vx} y2="534" />
              ))}
              {[438, 462, 486, 510].map((hy) => (
                <line key={hy} x1={x} y1={hy} x2={x + 72} y2={hy} />
              ))}
            </g>
            <rect x={x - 4} y="534" width="80" height="8" fill="#180d07" />
          </g>
        ))}
        {/* 屋顶 */}
        <path d="M212,292 Q300,326 392,366 L392,384 L32,384 L32,366 Q124,326 212,292 Z" fill="#100c09" />
        <path d="M212,292 Q150,320 80,352" fill="none" stroke="#4a6a78" strokeWidth="3" opacity="0.28" />
        <g stroke="#000" strokeWidth="1.6" opacity="0.35">
          <path d="M212,306 Q290,334 368,366" fill="none" />
          <path d="M212,320 Q280,342 344,366" fill="none" />
          <path d="M212,306 Q134,334 56,366" fill="none" />
          <path d="M212,320 Q144,342 80,366" fill="none" />
        </g>
        {/* 檐口（起翘） */}
        <path d="M18,384 Q212,360 406,384 L398,400 Q212,378 26,400 Z" fill="#1c130c" />
        <path d="M18,384 Q6,372 12,358 Q20,372 30,380 Z" fill="#1c130c" />
        <path d="M406,384 Q418,372 412,358 Q404,372 394,380 Z" fill="#1c130c" />
        {/* 正脊 */}
        <rect x="204" y="278" width="16" height="16" fill="#1c130c" />
        <circle cx="212" cy="274" r="6" fill="#241610" />
        {/* 檐下小灯笼 */}
        <g className="nhs-lantern">
          <line x1="330" y1="404" x2="330" y2="420" stroke="#0a0a0a" strokeWidth="3" />
          <circle cx="330" cy="442" r="26" fill="url(#nhs-lantern-halo)" />
          <rect x="318" y="422" width="24" height="36" rx="11" fill="url(#nhs-lantern-body)" />
          <rect x="322" y="418" width="16" height="6" rx="2" fill="#2a170e" />
          <rect x="322" y="458" width="16" height="6" rx="2" fill="#2a170e" />
        </g>
      </g>

      {/* ============ 大灯笼（灯架） ============ */}
      <g>
        <rect x="474" y="296" width="10" height="252" fill="#140d08" />
        <rect x="460" y="544" width="38" height="12" fill="#0f0a07" />
        <rect x="414" y="296" width="70" height="9" fill="#140d08" />
        <line x1="430" y1="305" x2="430" y2="330" stroke="#0c0805" strokeWidth="4" />
        <g className="nhs-lantern">
          <circle cx="430" cy="400" r="98" fill="url(#nhs-lantern-halo)" />
          <rect x="386" y="332" width="88" height="136" rx="42" fill="url(#nhs-lantern-body)" />
          <g stroke="#b45f1d" strokeWidth="2" opacity="0.45" fill="none">
            <path d="M408,336 Q400,400 408,464" />
            <path d="M452,336 Q460,400 452,464" />
          </g>
          <rect x="398" y="322" width="64" height="12" rx="4" fill="#2a170e" />
          <rect x="398" y="466" width="64" height="12" rx="4" fill="#2a170e" />
          <text x="430" y="386" textAnchor="middle" fontSize="30" fill="#8a2f1a" fontFamily="serif" fontWeight="700">天</text>
          <text x="430" y="424" textAnchor="middle" fontSize="30" fill="#8a2f1a" fontFamily="serif" fontWeight="700">机</text>
          <line x1="430" y1="478" x2="430" y2="506" stroke="#c97e2b" strokeWidth="3" />
          <circle cx="430" cy="512" r="5" fill="#c97e2b" />
        </g>
      </g>

      {/* ============ 书案（书 + 卷轴） ============ */}
      <g>
        <rect x="60" y="516" width="200" height="10" fill="#241610" />
        {[72, 128, 196, 248].map((x) => (
          <rect key={x} x={x} y="526" width="9" height="24" fill="#170e08" />
        ))}
        <rect x="84" y="496" width="76" height="20" rx="2" fill="#1d2a3a" />
        <rect x="84" y="496" width="76" height="5" fill="#d8cfae" opacity="0.75" />
        <rect x="92" y="478" width="64" height="18" rx="2" fill="#4a2c1a" />
        <rect x="92" y="478" width="64" height="4" fill="#d8cfae" opacity="0.7" />
        <rect x="172" y="482" width="96" height="20" rx="10" fill="#d9cba4" />
        <circle cx="172" cy="492" r="10" fill="#b09a6a" />
        <circle cx="268" cy="492" r="10" fill="#b09a6a" />
        <line x1="196" y1="482" x2="196" y2="502" stroke="#8a6f42" strokeWidth="2.5" />
      </g>

      {/* ============ 梅枝（左上） ============ */}
      <g fill="none" stroke="#0c0906" strokeLinecap="round">
        <path d="M-30,64 Q100,42 230,92 Q330,128 424,106" strokeWidth="8" />
        <path d="M118,68 Q178,98 238,158" strokeWidth="5" />
        <path d="M228,92 Q298,90 362,128" strokeWidth="4" />
        <path d="M170,84 Q200,60 244,52" strokeWidth="3" />
        <path d="M300,108 Q330,96 368,98" strokeWidth="2.6" />
      </g>
      <g>
        {BLOSSOMS_D.map(([x, y, s], i) => (
          <Blossom key={i} x={x} y={y} s={s} />
        ))}
        <Bud x={36} y={72} /> <Bud x={150} y={60} s={0.9} /> <Bud x={262} y={100} />
        <Bud x={340} y={116} s={0.9} /> <Bud x={200} y={140} /> <Bud x={96} y={88} s={0.85} />
      </g>

      {/* ============ 露台栏杆（前景） ============ */}
      <g>
        <rect x="0" y="584" width="1440" height="14" fill="#0a0d11" />
        <rect x="0" y="584" width="1440" height="3" fill="#26363f" opacity="0.85" />
        {Array.from({ length: 32 }, (_, i) => 22 + i * 45).map((x) => (
          <rect key={x} x={x} y="598" width="9" height="34" fill="#0d1116" />
        ))}
        <rect x="0" y="632" width="1440" height="8" fill="#070a0d" />
        {[180, 640, 1100, 1330].map((x) => (
          <rect key={x} x={x} y="580" width="14" height="52" fill="#0a0d11" />
        ))}
      </g>

      {/* 暗角 */}
      <rect x="0" y="0" width="1440" height="640" fill="url(#nhs-vignette)" />
    </svg>
  );
}

const STARS_M: Array<[number, number, number, number]> = [
  [40, 60, 1.5, 0.7], [120, 130, 1.2, 0.5], [200, 60, 1.6, 0.75], [260, 180, 1.1, 0.45],
  [340, 220, 1.4, 0.6], [90, 200, 1.2, 0.5], [170, 240, 1.1, 0.4], [320, 40, 1.3, 0.55],
  [60, 300, 1.2, 0.45], [230, 280, 1.4, 0.55], [360, 300, 1.2, 0.5], [140, 90, 1.1, 0.4],
];

const SHORE_M: Array<[number, number]> = [
  [60, 434], [110, 430], [160, 435], [210, 431], [350, 433], [30, 431], [250, 435],
];

const BLOSSOMS_M: Array<[number, number, number]> = [
  [50, 58, 1], [105, 48, 0.85], [160, 66, 1.05], [215, 82, 0.9], [262, 82, 0.8],
  [80, 80, 0.75], [135, 95, 0.9], [190, 105, 0.8],
];

function MobileScene() {
  return (
    <svg
      className="night-hero-scene"
      viewBox="0 0 390 720"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <linearGradient id="mhs-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0e2431" />
          <stop offset="0.55" stopColor="#0a1a23" />
          <stop offset="1" stopColor="#060f14" />
        </linearGradient>
        <radialGradient id="mhs-moon-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#f6eecf" stopOpacity="0.4" />
          <stop offset="0.55" stopColor="#f6eecf" stopOpacity="0.13" />
          <stop offset="1" stopColor="#f6eecf" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="mhs-moon" cx="0.42" cy="0.38" r="0.75">
          <stop offset="0" stopColor="#fdf6dd" />
          <stop offset="0.8" stopColor="#f2e2b4" />
          <stop offset="1" stopColor="#e3cd96" />
        </radialGradient>
        <linearGradient id="mhs-lake" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0e2733" />
          <stop offset="1" stopColor="#050d12" />
        </linearGradient>
        <linearGradient id="mhs-refl" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f2e3b0" stopOpacity="0.55" />
          <stop offset="1" stopColor="#f2e3b0" stopOpacity="0" />
        </linearGradient>
        <radialGradient id="mhs-lantern-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#f5b545" stopOpacity="0.5" />
          <stop offset="1" stopColor="#f5b545" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="mhs-lantern-body" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f8c463" />
          <stop offset="0.55" stopColor="#f0a83e" />
          <stop offset="1" stopColor="#d67f27" />
        </linearGradient>
        <linearGradient id="mhs-wood" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#2e1c12" />
          <stop offset="0.5" stopColor="#1c100a" />
          <stop offset="1" stopColor="#120a06" />
        </linearGradient>
        <radialGradient id="mhs-window" cx="0.5" cy="0.45" r="0.75">
          <stop offset="0" stopColor="#f6bd63" />
          <stop offset="0.7" stopColor="#d98a35" />
          <stop offset="1" stopColor="#a85a1c" />
        </radialGradient>
        <radialGradient id="mhs-vignette" cx="0.5" cy="0.44" r="0.9">
          <stop offset="0.55" stopColor="#04090c" stopOpacity="0" />
          <stop offset="1" stopColor="#04090c" stopOpacity="0.5" />
        </radialGradient>
        <filter id="mhs-ink" x="-8%" y="-8%" width="116%" height="116%">
          <feTurbulence type="fractalNoise" baseFrequency="0.03 0.06" numOctaves="2" seed="7" result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale="10" />
        </filter>
        <filter id="mhs-soft" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="6" />
        </filter>
      </defs>

      <rect x="0" y="0" width="390" height="720" fill="url(#mhs-sky)" />
      <g fill="#dfe9e4">
        {STARS_M.map(([x, y, r, o], i) => (
          <circle key={i} cx={x} cy={y} r={r} opacity={o} />
        ))}
      </g>

      {/* 月（右上，手机可见） */}
      <circle cx="298" cy="102" r="76" fill="url(#mhs-moon-halo)" />
      <circle cx="298" cy="102" r="38" fill="url(#mhs-moon)" />
      <circle cx="286" cy="92" r="6" fill="#d9c28c" opacity="0.5" />
      <circle cx="310" cy="114" r="4.5" fill="#d9c28c" opacity="0.45" />

      {/* 远山 / 中山 */}
      <g filter="url(#mhs-ink)" opacity="0.9">
        <path
          d="M0,372 L40,332 L90,360 L140,326 L190,362 L240,334 L290,364 L340,336 L390,360 L390,420 L0,420 Z"
          fill="#1e3d47"
        />
      </g>
      <g filter="url(#mhs-ink)">
        <path
          d="M0,414 L50,384 L110,410 L170,382 L230,410 L290,386 L350,408 L390,394 L390,450 L0,450 Z"
          fill="#12262e"
        />
      </g>

      {/* 湖 + 月影 + 灯火 */}
      <rect x="0" y="430" width="390" height="120" fill="url(#mhs-lake)" />
      <rect x="272" y="432" width="52" height="112" fill="url(#mhs-refl)" opacity="0.55" />
      <g stroke="#e9d9a6" strokeWidth="2.2" strokeLinecap="round">
        {[
          [440, 40, 0.32], [452, 34, 0.27], [466, 28, 0.22],
          [480, 23, 0.17], [494, 18, 0.12], [508, 14, 0.08],
        ].map(([y, hw, o], i) => (
          <line key={i} x1={298 - hw} y1={y} x2={298 + hw} y2={y} opacity={o} />
        ))}
      </g>
      <g>
        {SHORE_M.map(([x, y], i) => (
          <g key={i}>
            <circle cx={x} cy={y} r="6" fill="#f0b95a" opacity="0.28" />
            <circle cx={x} cy={y} r="2.2" fill="#f6c86a" opacity="0.9" />
          </g>
        ))}
      </g>
      <ellipse className="nhs-mist" cx="190" cy="424" rx="200" ry="18" fill="#dfe9e4" opacity="0.07" filter="url(#mhs-soft)" />

      {/* 近岸 */}
      <g filter="url(#mhs-ink)">
        <path d="M0,560 L80,540 L160,556 L260,542 L390,556 L390,600 L0,600 Z" fill="#0a151b" />
      </g>

      {/* 楼阁（手机：完整但紧凑） */}
      <g>
        <rect x="8" y="560" width="192" height="18" fill="#1c130d" />
        <rect x="8" y="560" width="192" height="3" fill="#3d2c1e" opacity="0.9" />
        {[36, 108].map((x) => (
          <g key={x}>
            <rect x={x} y="430" width="14" height="130" fill="url(#mhs-wood)" />
            <rect x={x} y="430" width="3" height="130" fill="#5a4028" opacity="0.35" />
            <rect x={x - 4} y="552" width="22" height="9" fill="#0f0a07" />
          </g>
        ))}
        <rect x="24" y="416" width="160" height="16" fill="#241610" />
        <rect x="24" y="416" width="160" height="2.5" fill="#4a3320" opacity="0.7" />
        {[36, 108].map((x) => (
          <g key={x} fill="#2e1c10">
            <rect x={x - 7} y="404" width="28" height="12" rx="2" />
            <rect x={x - 3} y="397" width="20" height="9" rx="2" />
          </g>
        ))}
        <g>
          <rect x="52" y="442" width="56" height="100" fill="url(#mhs-window)" opacity="0.95" />
          <rect x="52" y="442" width="56" height="100" fill="none" stroke="#180d07" strokeWidth="6" />
          <g stroke="#2a170e" strokeWidth="2.2" opacity="0.9">
            {[66, 80, 94].map((vx) => (
              <line key={vx} x1={vx} y1="442" x2={vx} y2="542" />
            ))}
            {[462, 482, 502, 522].map((hy) => (
              <line key={hy} x1="52" y1={hy} x2="108" y2={hy} />
            ))}
          </g>
          <rect x="48" y="542" width="64" height="7" fill="#180d07" />
        </g>
        <path d="M104,356 Q150,382 198,408 L198,422 L10,422 L10,408 Q58,382 104,356 Z" fill="#100c09" />
        <path d="M104,356 Q76,376 44,396" fill="none" stroke="#4a6a78" strokeWidth="2.4" opacity="0.28" />
        <g stroke="#000" strokeWidth="1.3" opacity="0.35">
          <path d="M104,368 Q140,386 176,404" fill="none" />
          <path d="M104,380 Q132,394 162,406" fill="none" />
          <path d="M104,368 Q68,386 32,404" fill="none" />
        </g>
        <path d="M2,422 Q104,404 206,422 L200,433 Q104,417 8,433 Z" fill="#1c130c" />
        <path d="M2,422 Q-6,412 0,402 Q6,412 12,419 Z" fill="#1c130c" />
        <path d="M206,422 Q214,412 208,402 Q202,412 196,419 Z" fill="#1c130c" />
        <rect x="98" y="344" width="12" height="13" fill="#1c130c" />
        <circle cx="104" cy="341" r="4.5" fill="#241610" />
        <g className="nhs-lantern">
          <line x1="152" y1="432" x2="152" y2="446" stroke="#0a0a0a" strokeWidth="2.5" />
          <circle cx="152" cy="464" r="20" fill="url(#mhs-lantern-halo)" />
          <rect x="142" y="448" width="20" height="30" rx="9" fill="url(#mhs-lantern-body)" />
        </g>
      </g>

      {/* 大灯笼（手机：右下角，完全避开按钮） */}
      <g transform="translate(0 160)">
        <rect x="341" y="360" width="8" height="188" fill="#140d08" />
        <rect x="329" y="544" width="32" height="10" fill="#0f0a07" />
        <rect x="287" y="360" width="62" height="7" fill="#140d08" />
        <line x1="315" y1="367" x2="315" y2="388" stroke="#0c0805" strokeWidth="3.5" />
        <g className="nhs-lantern">
          <circle cx="315" cy="448" r="70" fill="url(#mhs-lantern-halo)" opacity="0.8" />
          <rect x="277" y="390" width="76" height="118" rx="36" fill="url(#mhs-lantern-body)" />
          <g stroke="#b45f1d" strokeWidth="1.8" opacity="0.45" fill="none">
            <path d="M295,394 Q289,448 295,504" />
            <path d="M335,394 Q341,448 335,504" />
          </g>
          <rect x="287" y="381" width="56" height="10" rx="3" fill="#2a170e" />
          <rect x="287" y="506" width="56" height="10" rx="3" fill="#2a170e" />
          <text x="315" y="436" textAnchor="middle" fontSize="25" fill="#8a2f1a" fontFamily="serif" fontWeight="700">天</text>
          <text x="315" y="470" textAnchor="middle" fontSize="25" fill="#8a2f1a" fontFamily="serif" fontWeight="700">机</text>
          <line x1="315" y1="516" x2="315" y2="540" stroke="#c97e2b" strokeWidth="2.5" />
          <circle cx="315" cy="545" r="4" fill="#c97e2b" />
        </g>
      </g>

      {/* 小书卷 */}
      <g>
        <rect x="24" y="588" width="56" height="15" rx="2" fill="#1d2a3a" />
        <rect x="24" y="588" width="56" height="4" fill="#d8cfae" opacity="0.7" />
        <rect x="30" y="574" width="46" height="14" rx="2" fill="#4a2c1a" />
      </g>

      {/* 梅枝 */}
      <g fill="none" stroke="#0c0906" strokeLinecap="round">
        <path d="M-20,52 Q80,34 170,74 Q230,96 282,84" strokeWidth="6" />
        <path d="M90,60 Q130,84 170,120" strokeWidth="4" />
        <path d="M170,74 Q220,74 262,94" strokeWidth="3.2" />
      </g>
      <g>
        {BLOSSOMS_M.map(([x, y, s], i) => (
          <Blossom key={i} x={x} y={y} s={s} />
        ))}
        <Bud x={28} y={58} /> <Bud x={120} y={52} s={0.9} /> <Bud x={205} y={82} />
        <Bud x={248} y={88} s={0.9} />
      </g>

      {/* 栏杆 */}
      <g>
        <rect x="0" y="674" width="390" height="12" fill="#0a0d11" />
        <rect x="0" y="674" width="390" height="2.5" fill="#26363f" opacity="0.85" />
        {Array.from({ length: 10 }, (_, i) => 14 + i * 38).map((x) => (
          <rect key={x} x={x} y="686" width="8" height="26" fill="#0d1116" />
        ))}
        <rect x="0" y="712" width="390" height="8" fill="#070a0d" />
      </g>

      <rect x="0" y="0" width="390" height="720" fill="url(#mhs-vignette)" />
    </svg>
  );
}

export function NightHeroScene() {
  return (
    <>
      <span className="nhs-desktop" aria-hidden="true">
        <DesktopScene />
      </span>
      <span className="nhs-mobile" aria-hidden="true">
        <MobileScene />
      </span>
    </>
  );
}
