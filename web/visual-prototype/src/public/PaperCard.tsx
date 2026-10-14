/**
 * TJ-008.7 宣纸质感大卡。
 * 以 approved-reference.webp 首页四张主卡为基准：米白纸面、顶部水墨小插画、
 * 右上角朱砂竖条印（「天机」竖排白文）、标题 + 副标题 + 说明 + 深色胶囊按钮。
 * 文案只用 scenarioProducts 的真实 name/tagline/description，不编造任何结论。
 */
import { Link } from "../shared/router";
import type { ScenarioProduct } from "./scenarioProducts";
import artSunrise from "../assets/night-home/art-sunrise.jpg";
import artPeach from "../assets/night-home/art-peach.jpg";
import artHorse from "../assets/night-home/art-horse.jpg";
import artMountains from "../assets/night-home/art-mountains.jpg";

export type PaperCardArt = "sunrise" | "peach" | "horse" | "mountains";

/**
 * 第三轮：卡片插画改用原创 AI 水墨（src/assets/night-home/），
 * 非 SVG 几何堆砌。文案仍只用 scenarioProducts 真实字段。
 */
const ART_SRC: Record<PaperCardArt, string> = {
  sunrise: artSunrise,
  peach: artPeach,
  horse: artHorse,
  mountains: artMountains,
};

const ART_ALT: Record<PaperCardArt, string> = {
  sunrise: "日出山峦水墨",
  peach: "桃花树水墨",
  horse: "策马人物水墨",
  mountains: "层峦山水水墨",
};

function CardArt({ art }: { art: PaperCardArt }) {
  return (
    <img
      className="paper-card-art-img"
      src={ART_SRC[art]}
      alt=""
      aria-hidden="true"
      loading="lazy"
      draggable={false}
    />
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

/**
 * 手机紧凑列表（第三轮）：按批准原图手机端样式，缩略图 + 标题 + 简短说明 + 右箭头。
 * 仅在窄屏显示（CSS 控制），桌面端隐藏。
 */
export function MobileCardRow({ product, art }: { product: ScenarioProduct; art: PaperCardArt }) {
  return (
    <Link
      href={product.href ?? "/"}
      className="mobile-card-row"
      aria-label={`进入${displayName(product)}`}
    >
      <span className="mobile-card-thumb" aria-hidden="true">
        <img src={ART_SRC[art]} alt="" loading="lazy" draggable={false} />
      </span>
      <span className="mobile-card-text">
        <strong>{displayName(product)}</strong>
        <small>{product.tagline}</small>
      </span>
      <span className="mobile-card-arrow" aria-hidden="true">›</span>
    </Link>
  );
}
