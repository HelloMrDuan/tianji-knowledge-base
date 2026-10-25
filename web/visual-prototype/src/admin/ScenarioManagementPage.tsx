import { useEffect, useMemo, useState } from "react";
import {
  SCENARIO_DOMAINS,
  SCENARIO_ROUTES,
  evaluateScenarioGate,
  type ScenarioRegistryEntry,
} from "./scenarioGate";
import "./modules.css";
import "./scenario-gate.css";

const apiBase = (import.meta.env.VITE_TIANJI_API_BASE || "").replace(/\/$/, "");

type CapabilitiesDomain = {
  domain: string;
  default_variant?: string;
  variants?: string[];
};

type PublishNotice = {
  scenarioId: string;
  kind: "refused" | "read-only";
  text: string;
};

/**
 * Scenario 管理（TJ-026.2）：真实场景数据页。
 *
 * Rows come from the live public /api/v1/scenarios registry — never from
 * the DEMO fixtures in modules.ts (the old scenarios demo module was
 * removed when this page landed). Variant values come from the live
 * /api/v1/capabilities response; a scenario without an engine domain
 * (dream, research state) honestly shows no production variant.
 *
 * Publish is read-only by design: there is no publish/write endpoint in
 * this admin surface, so the publish action performs NO network request.
 * A gate failure produces an explicit refusal listing the failed items;
 * a gate pass states the gate passed and that the publish write channel
 * is not connected. Neither path pretends a publish happened.
 */
export default function ScenarioManagementPage() {
  const [scenarios, setScenarios] = useState<ScenarioRegistryEntry[] | null>(null);
  const [variants, setVariants] = useState<Record<string, string>>({});
  const [loadError, setLoadError] = useState("");
  const [notices, setNotices] = useState<Record<string, PublishNotice>>({});

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const response = await fetch(`${apiBase}/api/v1/scenarios`);
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          throw new Error(`场景注册读取失败（HTTP ${response.status}）。`);
        }
        const list = Array.isArray(data?.scenarios) ? data.scenarios : [];
        if (!cancelled) setScenarios(list);
      } catch (err) {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : "场景注册读取失败。");
        }
      }
      try {
        const response = await fetch(`${apiBase}/api/v1/capabilities`);
        const data = await response.json().catch(() => ({}));
        if (response.ok && Array.isArray(data?.domains)) {
          const map: Record<string, string> = {};
          for (const entry of data.domains as CapabilitiesDomain[]) {
            if (entry.default_variant) map[entry.domain] = entry.default_variant;
          }
          if (!cancelled) setVariants(map);
        }
      } catch {
        // Variant display is best-effort; the gate does not depend on it.
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const rows = useMemo(
    () =>
      (scenarios ?? []).map((scenario) => ({
        scenario,
        route: SCENARIO_ROUTES[scenario.id] ?? "",
        variant: variants[SCENARIO_DOMAINS[scenario.id] ?? ""] ?? "",
        gate: evaluateScenarioGate(scenario),
      })),
    [scenarios, variants],
  );

  function publish(row: (typeof rows)[number]) {
    const { scenario, gate } = row;
    if (!gate.passed) {
      const failed = gate.items
        .filter((item) => !item.passed)
        .map((item) => `${item.label}（${item.detail}）`)
        .join("；");
      setNotices((prev) => ({
        ...prev,
        [scenario.id]: {
          scenarioId: scenario.id,
          kind: "refused",
          text: `发布被门禁拒绝：${failed}。`,
        },
      }));
      return;
    }
    setNotices((prev) => ({
      ...prev,
      [scenario.id]: {
        scenarioId: scenario.id,
        kind: "read-only",
        text: "门禁通过；发布写入通道未接入（当前只读管理，写入与发布服务待后续接入），未执行任何发布。",
      },
    }));
  }

  return (
    <section className="admin-card admin-scenario-page">
      <h1>Scenario 管理</h1>
      <p>
        以下场景来自真实场景注册（/api/v1/scenarios），门禁逐项核验路由、
        API 接通、结果页真实性与关键测试在册情况。门禁未通过的场景不得发布。
      </p>
      {loadError && (
        <p role="alert" className="governance-auth-error">
          {loadError}
        </p>
      )}
      {scenarios === null && !loadError && <p>正在读取真实场景注册…</p>}
      {scenarios !== null && (
        <table className="module-table admin-scenario-table">
          <caption>真实场景入口与发布门禁</caption>
          <thead>
            <tr>
              <th>场景</th>
              <th>前台路由</th>
              <th>注册状态</th>
              <th>引擎 variant</th>
              <th>发布门禁</th>
              <th>发布操作</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const notice = notices[row.scenario.id];
              return (
                <tr key={row.scenario.id} data-scenario-id={row.scenario.id}>
                  <td>
                    <strong>{row.scenario.name}</strong>
                    <br />
                    <small>{row.scenario.id}</small>
                  </td>
                  <td>{row.route || "未登记"}</td>
                  <td>
                    {row.scenario.status}
                    <br />
                    <small>{row.scenario.execution ?? "无执行通道"}</small>
                  </td>
                  <td>{row.variant || "—（研究态，无生产 variant）"}</td>
                  <td>
                    <strong
                      className={
                        row.gate.passed
                          ? "admin-gate-pass"
                          : "admin-gate-fail"
                      }
                    >
                      {row.gate.passed ? "门禁通过" : "门禁未通过"}
                    </strong>
                    <ul className="admin-gate-items">
                      {row.gate.items.map((item) => (
                        <li key={item.key}>
                          {item.passed ? "✓" : "✗"} {item.label}：{item.detail}
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="admin-button"
                      aria-label={`发布 ${row.scenario.name}`}
                      onClick={() => publish(row)}
                    >
                      发布
                    </button>
                    {notice && (
                      <p
                        role={notice.kind === "refused" ? "alert" : "status"}
                        className={
                          notice.kind === "refused"
                            ? "governance-auth-error"
                            : "admin-gate-note"
                        }
                      >
                        {notice.text}
                      </p>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}
