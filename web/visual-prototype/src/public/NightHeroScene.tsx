/**
 * TJ-008.7 第四轮：Hero 改用 <picture> + <source media>，确保按视口只加载一张图。
 * 仅在夜景主题下渲染（纸主题不请求夜景大图）。
 * 素材为本任务生成的原创水墨（src/assets/night-home/），非第三方图片。
 * 文字、按钮仍为真实 HTML/React 组件。纯装饰：aria-hidden。
 */
import { useEffect, useState } from "react";
import heroDesktop from "../assets/night-home/hero-desktop.jpg";
import heroMobile from "../assets/night-home/hero-mobile.jpg";
import { readTheme } from "./theme";

export function NightHeroScene() {
  const [isNight, setIsNight] = useState(() => readTheme() === "night");

  useEffect(() => {
    const el = document.documentElement;
    setIsNight(el.getAttribute("data-theme") !== "paper");
    const obs = new MutationObserver(() => {
      setIsNight(el.getAttribute("data-theme") !== "paper");
    });
    obs.observe(el, { attributes: true, attributeFilter: ["data-theme"] });
    return () => obs.disconnect();
  }, []);

  if (!isNight) return null;

  return (
    <picture className="night-hero-picture" aria-hidden="true">
      <source media="(max-width: 640px)" srcSet={heroMobile} />
      <img
        className="night-hero-painting"
        src={heroDesktop}
        alt=""
        draggable={false}
      />
    </picture>
  );
}
