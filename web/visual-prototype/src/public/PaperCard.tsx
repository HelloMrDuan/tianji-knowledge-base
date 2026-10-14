/**
 * TJ-008.7 宣纸质感大卡。
 * 以 approved-reference.webp 首页四张主卡为基准：米白纸面、顶部水墨小插画、
 * 右上角朱砂竖条印（「天机」竖排白文）、标题 + 副标题 + 说明 + 深色胶囊按钮。
 * 文案只用 scenarioProducts 的真实 name/tagline/description，不编造任何结论。
 */
import { Link } from "../shared/router";
import type { ScenarioProduct } from "./scenarioProducts";

export type PaperCardArt = "sunrise" | "peach" | "horse" | "mountains";

function MiniBlossom({ x, y, s = 1 }: { x: number; y: number; s?: number }) {
  const petals = [0, 72, 144, 216, 288];
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity="0.93">
      {petals.map((a) => (
        <ellipse key={a} cx="0" cy="-4.4" rx="2.9" ry="4.7" fill="#d98a94" opacity="0.9" transform={`rotate(${a})`} />
      ))}
      <circle r="1.6" fill="#a83a4e" />
    </g>
  );
}

function CardArt({ art }: { art: PaperCardArt }) {
  if (art === "sunrise") {
    // 日出山峦：暖阳 + 远近山影 + 雾 + 飞鸟
    return (
      <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
        <defs>
          <radialGradient id="pc-sun-glow" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0" stopColor="#e08a4e" stopOpacity="0.55" />
            <stop offset="1" stopColor="#e08a4e" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="80" cy="40" r="34" fill="url(#pc-sun-glow)" />
        <circle cx="80" cy="40" r="19" fill="#c96b3f" />
        <circle cx="80" cy="40" r="24" fill="none" stroke="#c96b3f" strokeWidth="1.4" opacity="0.45" />
        <circle cx="80" cy="40" r="29" fill="none" stroke="#c96b3f" strokeWidth="1" opacity="0.25" />
        {/* 远山 */}
        <path d="M6,66 L36,44 L58,58 L82,40 L108,60 L132,46 L154,64 L154,78 L6,78 Z" fill="#7d938a" opacity="0.75" />
        {/* 近山 */}
        <path d="M6,78 L44,54 L72,70 L100,52 L128,70 L154,58 L154,84 L6,84 Z" fill="#3c5a54" />
        <path d="M44,54 L56,62 L44,70" fill="none" stroke="#2c443f" strokeWidth="1.4" opacity="0.7" />
        <path d="M100,52 L112,60 L100,68" fill="none" stroke="#2c443f" strokeWidth="1.4" opacity="0.7" />
        {/* 山雾 */}
        <ellipse cx="80" cy="72" rx="62" ry="7" fill="#f6f1e2" opacity="0.65" />
        {/* 飞鸟 */}
        <g stroke="#3c5a54" strokeWidth="1.6" fill="none" opacity="0.7" strokeLinecap="round">
          <path d="M28,30 q4,-4 8,0 q4,-4 8,0" />
          <path d="M124,24 q3,-3 6,0 q3,-3 6,0" />
        </g>
        {/* 水面 */}
        <g stroke="#3c5a54" strokeWidth="1.6" opacity="0.45" strokeLinecap="round">
          <line x1="14" y1="88" x2="58" y2="88" />
          <line x1="70" y1="91" x2="118" y2="91" />
          <line x1="126" y1="88" x2="150" y2="88" />
        </g>
      </svg>
    );
  }
  if (art === "peach") {
    // 桃花树：曲干 + 繁枝 + 花簇 + 嫩叶
    const blooms: Array<[number, number, number]> = [
      [58, 30, 1.1], [72, 24, 0.9], [48, 22, 0.85], [86, 30, 1], [98, 22, 0.9],
      [128, 40, 1.05], [140, 32, 0.9], [118, 30, 0.85], [134, 22, 0.8],
      [104, 44, 0.9], [66, 44, 0.85], [40, 36, 0.8], [148, 46, 0.85],
    ];
    return (
      <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
        {/* 树干 */}
        <path d="M78,92 Q74,70 70,58 Q66,48 58,40" fill="none" stroke="#4a3b2c" strokeWidth="5" strokeLinecap="round" />
        <path d="M78,92 Q84,72 92,60" fill="none" stroke="#4a3b2c" strokeWidth="4" strokeLinecap="round" />
        <path d="M74,76 Q60,70 48,66" fill="none" stroke="#4a3b2c" strokeWidth="3" strokeLinecap="round" />
        {/* 枝 */}
        <g fill="none" stroke="#4a3b2c" strokeLinecap="round">
          <path d="M70,58 Q60,50 52,38" strokeWidth="2.6" />
          <path d="M68,52 Q76,42 84,34" strokeWidth="2.6" />
          <path d="M92,60 Q104,52 116,48" strokeWidth="2.6" />
          <path d="M94,54 Q106,44 118,36" strokeWidth="2.4" />
          <path d="M96,48 Q110,40 126,38" strokeWidth="2.4" />
          <path d="M60,40 Q54,32 50,26" strokeWidth="2" />
          <path d="M116,48 Q126,42 136,40" strokeWidth="2" />
        </g>
        {/* 树皮纹 */}
        <path d="M76,84 Q74,76 73,70" fill="none" stroke="#3a2d20" strokeWidth="1.2" opacity="0.7" />
        {/* 嫩叶 */}
        <g fill="#7d9a6a" opacity="0.85">
          <ellipse cx="62" cy="52" rx="4.5" ry="2.2" transform="rotate(-30 62 52)" />
          <ellipse cx="110" cy="56" rx="4.5" ry="2.2" transform="rotate(25 110 56)" />
          <ellipse cx="92" cy="38" rx="4" ry="2" transform="rotate(-15 92 38)" />
        </g>
        {/* 花簇 */}
        {blooms.map(([x, y, s], i) => (
          <MiniBlossom key={i} x={x} y={y} s={s} />
        ))}
        {/* 落英 */}
        <g fill="#d98a94" opacity="0.6">
          <ellipse cx="40" cy="80" rx="3" ry="2" transform="rotate(20 40 80)" />
          <ellipse cx="120" cy="76" rx="3" ry="2" transform="rotate(-15 120 76)" />
        </g>
      </svg>
    );
  }
  if (art === "horse") {
    // 策马扬蹄：腾跃之势 + 骑者持缨
    return (
      <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
        <defs>
          <linearGradient id="pc-horse" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#3a4644" />
            <stop offset="1" stopColor="#232d2c" />
          </linearGradient>
        </defs>
        <g fill="url(#pc-horse)">
          {/* 马身（前倾腾跃） */}
          <path d="M52,66 Q72,54 100,52 Q118,51 130,42 L134,49 Q122,60 102,63 Q76,68 56,70 Z" />
          {/* 马颈高昂 */}
          <path d="M118,52 Q130,40 138,26 L147,30 Q139,44 128,56 Z" />
          {/* 马头 */}
          <path d="M136,24 L149,27 L145,36 L133,32 Z" />
          <ellipse cx="140" cy="30" rx="2" ry="1.4" fill="#f6f1e2" opacity="0.7" />
          {/* 鬃毛飞扬 */}
          <path d="M120,50 Q110,40 108,30 Q116,38 124,44 Z" />
          <path d="M114,54 Q104,48 98,40 Q108,44 116,48 Z" opacity="0.8" />
          {/* 前腿扬起 */}
          <path d="M112,62 Q124,56 136,54 L138,60 Q126,63 114,68 Z" />
          <path d="M106,64 Q114,54 124,48 L128,53 Q120,60 112,69 Z" />
          {/* 后腿蹬地 */}
          <path d="M62,68 Q54,78 50,90 L44,88 Q48,76 56,66 Z" />
          <path d="M72,69 Q68,80 66,91 L60,90 Q62,79 66,68 Z" />
          {/* 马尾飘扬 */}
          <path d="M52,64 Q38,64 28,74 Q40,73 48,71 Q56,69 58,66 Z" />
          {/* 骑者：躯干前倾 */}
          <circle cx="92" cy="26" r="5.5" />
          <path d="M87,32 Q84,42 87,51 L97,51 Q97,42 98,33 Z" />
          {/* 骑者腿 */}
          <path d="M88,50 Q84,58 86,64 L92,63 Q91,57 93,51 Z" />
          {/* 持缨手臂 */}
          <path d="M97,36 L113,44 L111,49 L95,41 Z" />
        </g>
        {/* 缰绳 */}
        <path d="M113,44 Q126,40 137,29" fill="none" stroke="#232d2c" strokeWidth="2" />
        {/* 长缨 */}
        <path d="M97,36 Q90,28 82,24" fill="none" stroke="#8a2f1a" strokeWidth="2.2" strokeLinecap="round" />
        <circle cx="80" cy="23" r="2.6" fill="#8a2f1a" />
        {/* 尘烟动势 */}
        <g stroke="#3c5a54" strokeWidth="1.6" opacity="0.4" fill="none" strokeLinecap="round">
          <path d="M20,78 q10,-6 22,-4" />
          <path d="M28,86 q8,-5 18,-3" />
        </g>
        <path d="M10,92 L150,92" stroke="#3c5a54" strokeWidth="2" opacity="0.4" />
      </svg>
    );
  }
  // 山水：层峦 + 云雾 + 山间小阁 + 水面
  return (
    <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
      {/* 远山 */}
      <path d="M6,64 L34,42 L56,54 L78,38 L104,58 L126,44 L154,60 L154,74 L6,74 Z" fill="#8fa39b" opacity="0.8" />
      {/* 云雾 */}
      <ellipse cx="80" cy="62" rx="58" ry="6" fill="#f6f1e2" opacity="0.7" />
      {/* 近山 */}
      <path d="M6,78 L40,52 L66,68 L94,48 L122,68 L154,56 L154,84 L6,84 Z" fill="#3c5a54" />
      <path d="M40,52 L50,60 L40,68" fill="none" stroke="#2c443f" strokeWidth="1.4" opacity="0.7" />
      <path d="M94,48 L104,56 L94,64" fill="none" stroke="#2c443f" strokeWidth="1.4" opacity="0.7" />
      {/* 山间小阁 */}
      <g>
        <path d="M96,44 L104,38 L112,44 L110,45 L98,45 Z" fill="#2c3a37" />
        <rect x="99" y="45" width="10" height="8" fill="#2c3a37" />
        <rect x="101" y="47" width="6" height="4" fill="#c96b3f" opacity="0.8" />
      </g>
      {/* 松 */}
      <g stroke="#2c443f" strokeWidth="1.6" fill="none" opacity="0.85">
        <path d="M30,68 L30,58" />
        <path d="M30,60 q-6,-2 -9,1 M30,60 q6,-2 9,1 M30,64 q-5,-1 -8,2 M30,64 q5,-1 8,2" />
      </g>
      {/* 水面 */}
      <g stroke="#3c5a54" strokeWidth="1.6" opacity="0.5" strokeLinecap="round">
        <line x1="14" y1="88" x2="60" y2="88" />
        <line x1="72" y1="91" x2="120" y2="91" />
        <line x1="128" y1="88" x2="150" y2="88" />
      </g>
      {/* 日/月 */}
      <circle cx="126" cy="18" r="9" fill="none" stroke="#8a6a45" strokeWidth="2" />
      <circle cx="126" cy="18" r="12" fill="none" stroke="#8a6a45" strokeWidth="1" opacity="0.4" />
      {/* 飞鸟 */}
      <path d="M52,24 q3.5,-3.5 7,0 q3.5,-3.5 7,0" fill="none" stroke="#3c5a54" strokeWidth="1.5" opacity="0.65" strokeLinecap="round" />
    </svg>
  );
}

export function displayName(product: ScenarioProduct): string {
  return product.name.replace(" · 结构版", "").replace("流年结构", "流年运势");
}

export function PaperCard({ product, art }: { product: ScenarioProduct; art: PaperCardArt }) {
  return (
    <Link
      href={product.href ?? "/"}
      className="paper-card"
      aria-label={`进入${displayName(product)}`}
    >
      <span className="paper-card-seal" aria-hidden="true">天机</span>
      <span className="paper-card-art">
        <CardArt art={art} />
      </span>
      <h3 className="paper-card-title">{displayName(product)}</h3>
      <span className="paper-card-tagline">{product.tagline}</span>
      <p className="paper-card-desc">{product.description}</p>
      <span className="paper-card-btn">立即测算</span>
    </Link>
  );
}
