import { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { usePath } from "./shared/router";
import { PublicApp } from "./public/PublicApp";
import "./shared/base.css";

const AdminApp = lazy(() => import("./admin/AdminApp"));
function App() {
  const path = usePath();
  return path === "/admin" || path.startsWith("/admin/") ? (
    <Suspense
      fallback={<div className="loading-screen">正在打开管理工作台…</div>}
    >
      <AdminApp />
    </Suspense>
  ) : (
    <PublicApp />
  );
}
createRoot(document.getElementById("root")!).render(<App />);
