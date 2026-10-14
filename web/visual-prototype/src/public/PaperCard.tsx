/**
 * TJ-008.7 宣纸质感大卡。
 * 以 approved-reference.webp 首页四张主卡为基准：米白纸面、顶部水墨小插画、
 * 右上角朱砂竖条印（「天机」竖排白文）、标题 + 副标题 + 说明 + 深色胶囊按钮。
 * 文案只用 scenarioProducts 的真实 name/tagline/description，不编造任何结论。
 */
import { Link } from "../shared/router";
import type { ScenarioProduct } from "./scenarioProducts";

export type PaperCardArt = "sunrise" | "peach" | "horse" | "mountains";

function CardArt({ art }: { art: PaperCardArt }) {
  if (art === "sunrise") {
    // 日出山峦
    return (
      <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
        <circle cx="80" cy="42" r="20" fill="#c96b3f" />
        <circle cx="80" cy="42" r="26" fill="none" stroke="#c96b3f" strokeWidth="1.5" opacity="0.5" />
        <path d="M8,78 L52,44 L84,68 L112,40 L152,78" fill="none" stroke="#3c5a54" strokeWidth="3" strokeLinejoin="round" />
        <path d="M8,86 L152,86" stroke="#3c5a54" strokeWidth="2" opacity="0.5" />
        <path d="M28,90 L132,90" stroke="#3c5a54" strokeWidth="1.5" opacity="0.3" />
      </svg>
    );
  }
  if (art === "peach") {
    // 桃枝
    return (
      <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
        <path d="M18,88 Q70,70 96,40 Q112,22 142,18" fill="none" stroke="#4a3b2c" strokeWidth="3.5" strokeLinecap="round" />
        <path d="M70,66 Q60,52 62,40" fill="none" stroke="#4a3b2c" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M104,50 Q118,44 130,46" fill="none" stroke="#4a3b2c" strokeWidth="2.5" strokeLinecap="round" />
        <g fill="#d98a94">
          <circle cx="60" cy="36" r="7" />
          <circle cx="72" cy="30" r="6" />
          <circle cx="52" cy="28" r="5.5" />
          <circle cx="132" cy="44" r="7" />
          <circle cx="144" cy="36" r="6" />
          <circle cx="122" cy="34" r="5.5" />
          <circle cx="100" cy="34" r="6.5" />
          <circle cx="112" cy="24" r="5.5" />
        </g>
        <g fill="#b45f6a">
          <circle cx="60" cy="36" r="2.2" />
          <circle cx="132" cy="44" r="2.2" />
          <circle cx="100" cy="34" r="2.2" />
        </g>
      </svg>
    );
  }
  if (art === "horse") {
    // 策马人物剪影：修长马身 + 腾跃四肢 + 骑者
    return (
      <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
        <g fill="#2e3a38">
          {/* 马身：细长躯干 */}
          <path d="M42,60 Q66,50 96,54 Q114,56 124,48 L127,55 Q114,64 90,66 Q62,68 44,64 Z" />
          {/* 马颈昂起 */}
          <path d="M112,53 Q122,42 130,28 L138,32 Q130,46 120,57 Z" />
          {/* 马头 */}
          <path d="M128,26 L141,29 L137,37 L126,33 Z" />
          {/* 鬃毛 */}
          <path d="M112,51 Q104,42 103,33 Q110,41 117,47 Z" />
          {/* 前腿腾跃 */}
          <path d="M106,64 Q118,72 130,77 L127,82 Q114,77 103,70 Z" />
          <path d="M98,66 Q106,78 113,87 L107,89 Q100,80 94,70 Z" />
          {/* 后腿蹬伸 */}
          <path d="M54,64 Q46,74 42,85 L36,83 Q40,72 48,62 Z" />
          <path d="M64,66 Q60,76 58,87 L52,86 Q54,76 58,65 Z" />
          {/* 马尾飘扬 */}
          <path d="M42,59 Q30,61 21,71 Q31,69 39,67 Q45,65 47,61 Z" />
          {/* 骑者：头 + 躯干前倾 */}
          <circle cx="84" cy="28" r="5.5" />
          <path d="M79,34 Q76,44 79,53 L89,53 Q89,44 90,35 Z" />
          {/* 骑者手臂前伸持缰 */}
          <path d="M89,38 L105,46 L103,51 L87,43 Z" />
        </g>
        {/* 缰绳 */}
        <path d="M105,46 Q118,42 129,31" fill="none" stroke="#2e3a38" strokeWidth="2" />
        <path d="M10,90 L150,90" stroke="#3c5a54" strokeWidth="2" opacity="0.4" />
        <path d="M28,52 Q36,46 46,48" fill="none" stroke="#3c5a54" strokeWidth="1.5" opacity="0.4" />
      </svg>
    );
  }
  // 山水
  return (
    <svg viewBox="0 0 160 96" aria-hidden="true" focusable="false" className="paper-card-art-svg">
      <path d="M6,72 L44,34 L70,58 L96,28 L128,60 L154,44 L154,80 L6,80 Z" fill="none" stroke="#3c5a54" strokeWidth="3" strokeLinejoin="round" />
      <path d="M44,34 L56,46 L44,58" fill="none" stroke="#3c5a54" strokeWidth="1.5" opacity="0.6" />
      <path d="M96,28 L108,42 L96,54" fill="none" stroke="#3c5a54" strokeWidth="1.5" opacity="0.6" />
      <g stroke="#3c5a54" strokeWidth="1.8" opacity="0.55">
        <line x1="14" y1="86" x2="60" y2="86" />
        <line x1="72" y1="86" x2="120" y2="86" />
        <line x1="40" y1="92" x2="110" y2="92" opacity="0.6" />
      </g>
      <circle cx="126" cy="18" r="9" fill="none" stroke="#8a6a45" strokeWidth="2" />
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
