import { useEffect, useRef, useState } from "react";
import { Icon } from "../shared/Icon";

const preferenceKey = "tianji.prototype.music";
function savedPreferences() {
  try {
    const value = JSON.parse(localStorage.getItem(preferenceKey) || "{}");
    return {
      volume:
        typeof value.volume === "number" && Number.isFinite(value.volume)
          ? Math.max(0, Math.min(1, value.volume))
          : 0.25,
      optedIn: value.optedIn === true,
    };
  } catch {
    return { volume: 0.25, optedIn: false };
  }
}
export function MusicPlayer() {
  const [initial] = useState(savedPreferences);
  const [volume, setVolume] = useState(initial.volume);
  const [playing, setPlaying] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [optedIn, setOptedIn] = useState(initial.optedIn);
  const [error, setError] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
    try {
      localStorage.setItem(preferenceKey, JSON.stringify({ volume, optedIn }));
    } catch {
      /* Private browsing can disallow storage; sound remains usable. */
    }
  }, [volume, optedIn]);
  useEffect(() => {
    const audio = audioRef.current;
    return () => {
      audio?.pause();
    };
  }, []);
  const pauseByChoice = () => {
    audioRef.current?.pause();
    setOptedIn(false);
  };
  const toggle = async () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (!audio.paused) {
      pauseByChoice();
      return;
    }
    try {
      await audio.play();
      setOptedIn(true);
      setError(false);
    } catch {
      setError(true);
    }
  };
  return (
    <div className={`music-player ${playing ? "is-playing" : ""}`}>
      <audio
        ref={audioRef}
        src="/music/quiet-waters.ogg"
        loop
        preload="none"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onError={() => setError(true)}
      />
      <button
        className="music-trigger"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        aria-label="背景音乐设置"
      >
        <Icon name="music" size={18} />
        <span>听一曲</span>
        {playing && (
          <span className="sound-bars" aria-label="正在播放">
            <i />
            <i />
            <i />
          </span>
        )}
      </button>
      {playing && (
        <button
          className="music-global-pause icon-button"
          aria-label="全局暂停音乐"
          onClick={pauseByChoice}
        >
          <Icon name="pause" size={16} />
        </button>
      )}
      {expanded && (
        <section className="music-popover" aria-label="背景音乐控制">
          <div className="music-title">
            <span className="music-art">弦</span>
            <div>
              <strong>静水弦音</strong>
              <small>原创合成弦音 · 循环</small>
            </div>
            <button
              className="icon-button"
              aria-label="关闭音乐设置"
              onClick={() => setExpanded(false)}
            >
              <Icon name="close" size={16} />
            </button>
          </div>
          <p>
            {error
              ? "音乐暂时无法播放，请稍后重试。"
              : playing
                ? "让声音轻一些，让思绪静一些。"
                : optedIn
                  ? "已记住你的音量，点击后继续播放。"
                  : "默认关闭，播放由你决定。"}
          </p>
          <div className="music-controls">
            <button
              className="music-play"
              onClick={toggle}
              aria-label={playing ? "暂停背景音乐" : "播放背景音乐"}
            >
              <Icon name={playing ? "pause" : "play"} size={17} />
              {playing ? "暂停" : "播放"}
            </button>
            <Icon name="volume" size={17} />
            <input
              type="range"
              aria-label="背景音乐音量"
              min="0"
              max="1"
              step="0.05"
              value={volume}
              onChange={(e) => setVolume(Number(e.target.value))}
            />
          </div>
        </section>
      )}
    </div>
  );
}
