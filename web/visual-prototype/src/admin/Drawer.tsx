import { useEffect, useId, useRef } from "react";
import type { ReactNode } from "react";
import { Icon } from "../shared/Icon";

/**
 * B020 TJ-026.1 layout only: side drawer panel (new component).
 *
 * Unlike the shared centered Dialog, a drawer docks to the right edge
 * so the list underneath stays visible — the #87 shell (sidebar +
 * table) is never replaced by a detail view. Same conventions as
 * Dialog: Escape closes, backdrop click closes, focus moves to the
 * close button on open and returns on close, body scroll locks while
 * open. No data logic lives here; callers render content as children.
 */
export function Drawer({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  const id = useId();
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
      previous?.focus();
    };
  }, [onClose]);
  return (
    <>
      <button
        className="admin-drawer-backdrop"
        aria-label="关闭详情"
        onClick={onClose}
      />
      <aside
        className="admin-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby={id}
      >
        <header className="admin-drawer-head">
          <h2 id={id}>{title}</h2>
          <button
            ref={closeRef}
            aria-label="关闭详情"
            className="icon-button"
            onClick={onClose}
          >
            <Icon name="close" />
          </button>
        </header>
        <div className="admin-drawer-body">{children}</div>
      </aside>
    </>
  );
}
