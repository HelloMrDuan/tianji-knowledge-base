/**
 * TJ-008.7 首页深青夜景：全幅 SVG 夜景。
 * 以 docs/product/designs/night-ink/approved-reference.webp 左上「首页·桌面端」为基准：
 * 圆月、层叠远山、湖面倒影、左侧楼阁剪影、暖光灯笼、薄雾，深青底色 #0b1c23 系。
 * 纯装饰：aria-hidden；动画仅作氛围点缀，prefers-reduced-motion 下静态。
 */
export function NightHeroScene() {
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
          <stop offset="0" stopColor="#123039" />
          <stop offset="0.55" stopColor="#0b1c23" />
          <stop offset="1" stopColor="#081418" />
        </linearGradient>
        <radialGradient id="nhs-moon-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#f6eecf" stopOpacity="0.35" />
          <stop offset="0.6" stopColor="#f6eecf" stopOpacity="0.12" />
          <stop offset="1" stopColor="#f6eecf" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="nhs-lantern-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#f5b545" stopOpacity="0.55" />
          <stop offset="1" stopColor="#f5b545" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="nhs-lake" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0e2530" />
          <stop offset="1" stopColor="#081418" />
        </linearGradient>
        <linearGradient id="nhs-lantern-body" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f7c05e" />
          <stop offset="1" stopColor="#dd8f2f" />
        </linearGradient>
      </defs>

      {/* 夜空 */}
      <rect x="0" y="0" width="1440" height="640" fill="url(#nhs-sky)" />

      {/* 星 */}
      <g fill="#dfe9e4">
        <circle cx="80" cy="60" r="1.6" opacity="0.7" />
        <circle cx="210" cy="140" r="1.2" opacity="0.5" />
        <circle cx="340" cy="70" r="1.8" opacity="0.8" />
        <circle cx="470" cy="150" r="1.1" opacity="0.4" />
        <circle cx="590" cy="60" r="1.5" opacity="0.65" />
        <circle cx="700" cy="130" r="1.2" opacity="0.5" />
        <circle cx="820" cy="50" r="1.7" opacity="0.75" />
        <circle cx="940" cy="160" r="1.1" opacity="0.45" />
        <circle cx="1030" cy="60" r="1.4" opacity="0.6" />
        <circle cx="1290" cy="220" r="1.3" opacity="0.55" />
        <circle cx="1380" cy="90" r="1.6" opacity="0.7" />
        <circle cx="150" cy="240" r="1.2" opacity="0.45" />
        <circle cx="520" cy="230" r="1.4" opacity="0.55" />
        <circle cx="760" cy="210" r="1.1" opacity="0.4" />
        <circle cx="80" cy="330" r="1.3" opacity="0.5" />
        <circle cx="1330" cy="330" r="1.2" opacity="0.45" />
      </g>

      {/* 圆月（右上） */}
      <circle cx="1150" cy="112" r="120" fill="url(#nhs-moon-halo)" />
      <circle cx="1150" cy="112" r="56" fill="#f6eecf" />
      <circle cx="1132" cy="98" r="10" fill="#e8dcba" opacity="0.7" />
      <circle cx="1162" cy="126" r="7" fill="#e8dcba" opacity="0.6" />
      <circle cx="1148" cy="132" r="5" fill="#e8dcba" opacity="0.5" />

      {/* 远山（两层） */}
      <path
        d="M0,430 L120,340 L240,400 L360,300 L480,390 L620,320 L760,410 L900,330 L1040,400 L1180,310 L1320,390 L1440,340 L1440,475 L0,475 Z"
        fill="#16333c"
        opacity="0.9"
      />
      <path
        d="M0,470 L100,400 L220,450 L340,380 L470,460 L600,400 L740,470 L880,410 L1020,465 L1160,400 L1300,460 L1440,415 L1440,505 L0,505 Z"
        fill="#0f2530"
      />

      {/* 湖面与月影 */}
      <rect x="0" y="470" width="1440" height="170" fill="url(#nhs-lake)" />
      <ellipse cx="1150" cy="545" rx="42" ry="58" fill="#f6eecf" opacity="0.14" />
      <g fill="#f6eecf" opacity="0.12">
        <rect x="1108" y="510" width="84" height="4" rx="2" />
        <rect x="1118" y="528" width="64" height="4" rx="2" />
        <rect x="1112" y="548" width="76" height="4" rx="2" />
        <rect x="1122" y="568" width="56" height="4" rx="2" />
      </g>

      {/* 左侧楼阁剪影 */}
      <g fill="#0a151b">
        <rect x="60" y="452" width="264" height="18" />
        <rect x="92" y="358" width="14" height="94" />
        <rect x="276" y="358" width="14" height="94" />
        <rect x="150" y="380" width="80" height="72" />
        <path d="M52,362 Q192,296 332,362 L312,362 Q192,316 72,362 Z" />
        <path d="M40,360 Q60,352 84,358 L60,368 Z" />
        <path d="M344,360 Q324,352 300,358 L324,368 Z" />
        <rect x="142" y="278" width="10" height="58" />
        <rect x="232" y="278" width="10" height="58" />
        <path d="M112,284 Q192,232 272,284 L254,284 Q192,250 130,284 Z" />
        <path d="M104,282 Q120,276 138,280 L118,290 Z" />
        <path d="M280,282 Q264,276 246,280 L266,290 Z" />
        <rect x="186" y="212" width="8" height="30" />
        <circle cx="190" cy="206" r="6" />
        <path d="M150,244 Q190,224 230,244 L216,244 Q190,232 164,244 Z" />
      </g>
      {/* 楼阁暖窗 */}
      <g fill="#f5b545">
        <rect x="118" y="392" width="34" height="46" opacity="0.55" />
        <rect x="228" y="392" width="34" height="46" opacity="0.55" />
        <rect x="164" y="392" width="52" height="46" opacity="0.3" />
      </g>
      <g stroke="#0a151b" strokeWidth="3">
        <line x1="135" y1="392" x2="135" y2="438" />
        <line x1="245" y1="392" x2="245" y2="438" />
        <line x1="190" y1="392" x2="190" y2="438" />
      </g>

      {/* 暖光灯笼 ×3 */}
      <g className="nhs-lantern">
        <circle cx="380" cy="300" r="52" fill="url(#nhs-lantern-halo)" />
        <line x1="380" y1="238" x2="380" y2="268" stroke="#0a151b" strokeWidth="5" />
        <rect x="358" y="268" width="44" height="60" rx="20" fill="url(#nhs-lantern-body)" />
        <rect x="366" y="260" width="28" height="10" rx="3" fill="#0a151b" />
        <rect x="366" y="328" width="28" height="10" rx="3" fill="#0a151b" />
        <line x1="380" y1="338" x2="380" y2="366" stroke="#c97e2b" strokeWidth="3" />
        <circle cx="380" cy="372" r="5" fill="#c97e2b" />
        <text x="380" y="308" textAnchor="middle" fontSize="22" fill="#7a3d12" fontFamily="serif">福</text>
      </g>
      <g className="nhs-lantern">
        {/* 中部灯笼右移，避开中央说明文字区 */}
        <circle cx="1160" cy="450" r="44" fill="url(#nhs-lantern-halo)" />
        <rect x="1156" y="460" width="8" height="70" fill="#0a151b" />
        <line x1="1160" y1="422" x2="1160" y2="434" stroke="#0a151b" strokeWidth="4" />
        <rect x="1140" y="434" width="40" height="52" rx="18" fill="url(#nhs-lantern-body)" />
        <rect x="1148" y="427" width="24" height="9" rx="3" fill="#0a151b" />
        <rect x="1148" y="486" width="24" height="9" rx="3" fill="#0a151b" />
      </g>
      <g className="nhs-lantern">
        <circle cx="1330" cy="400" r="44" fill="url(#nhs-lantern-halo)" />
        <rect x="1326" y="410" width="8" height="90" fill="#0a151b" />
        <line x1="1330" y1="372" x2="1330" y2="384" stroke="#0a151b" strokeWidth="4" />
        <rect x="1310" y="384" width="40" height="52" rx="18" fill="url(#nhs-lantern-body)" />
        <rect x="1318" y="377" width="24" height="9" rx="3" fill="#0a151b" />
        <rect x="1318" y="436" width="24" height="9" rx="3" fill="#0a151b" />
      </g>

      {/* 薄雾 */}
      <ellipse className="nhs-mist nhs-mist-1" cx="420" cy="486" rx="330" ry="24" fill="#dfe9e4" opacity="0.07" />
      <ellipse className="nhs-mist nhs-mist-2" cx="1020" cy="505" rx="390" ry="28" fill="#dfe9e4" opacity="0.05" />

      {/* 前景暗角 */}
      <path d="M0,640 L0,566 Q200,522 390,584 L390,640 Z" fill="#081216" />
      <path d="M1440,640 L1440,580 Q1300,548 1180,592 L1180,640 Z" fill="#081216" opacity="0.9" />
    </svg>
  );
}
