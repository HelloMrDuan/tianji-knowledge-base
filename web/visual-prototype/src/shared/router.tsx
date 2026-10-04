import { createContext, useContext, useSyncExternalStore } from "react";
import type { AnchorHTMLAttributes, ReactNode } from "react";

const event = "tianji:navigation";
const subscribe = (listener: () => void) => {
  window.addEventListener("popstate", listener);
  window.addEventListener(event, listener);
  return () => {
    window.removeEventListener("popstate", listener);
    window.removeEventListener(event, listener);
  };
};
export function usePath() {
  return useSyncExternalStore(subscribe, () => location.pathname);
}
export function navigate(path: string) {
  history.pushState(null, "", path);
  window.dispatchEvent(new Event(event));
  window.scrollTo({ top: 0, behavior: "instant" });
}
export function Link({
  href,
  children,
  onClick,
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) {
  return (
    <a
      {...props}
      href={href}
      onClick={(e) => {
        onClick?.(e);
        if (
          !e.defaultPrevented &&
          e.button === 0 &&
          !e.ctrlKey &&
          !e.metaKey &&
          !e.altKey &&
          !e.shiftKey &&
          href.startsWith("/") &&
          !href.includes("#")
        ) {
          e.preventDefault();
          navigate(href);
        }
      }}
    >
      {children}
    </a>
  );
}
export const NoticeContext = createContext<(text: string) => void>(() => {});
export function useNotice() {
  return useContext(NoticeContext);
}
export type Children = { children: ReactNode };
