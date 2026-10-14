/**
 * TJ-008.7 第三轮：Hero 改用原创 AI 水墨绘景（src/assets/night-home/）。
 * 素材为本任务生成的原创图片，非第三方受保护图片，更非设计参考截图。
 * 桌面 / 手机各一张独立构图；文字、按钮仍为真实 HTML/React 组件。
 * 纯装饰：aria-hidden。
 */
import heroDesktop from "../assets/night-home/hero-desktop.jpg";
import heroMobile from "../assets/night-home/hero-mobile.jpg";

export function NightHeroScene() {
  return (
    <>
      <span className="nhs-desktop" aria-hidden="true">
        <img
          className="night-hero-painting"
          src={heroDesktop}
          alt=""
          draggable={false}
        />
      </span>
      <span className="nhs-mobile" aria-hidden="true">
        <img
          className="night-hero-painting"
          src={heroMobile}
          alt=""
          draggable={false}
        />
      </span>
    </>
  );
}
