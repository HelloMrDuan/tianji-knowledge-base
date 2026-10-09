export type ExecuteResponse = {
  domain: string;
  variant: string;
  mode: "production" | "research";
  deterministic: boolean;
  chart: Record<string, any>;
  rule_matches: Array<Record<string, any>>;
  trace: Array<Record<string, any>>;
  evidence: Record<string, Record<string, any>>;
  warnings: string[];
  limitations: string[];
  explanation: Record<string, any> | null;
  explanation_status: "disabled" | "succeeded" | "failed";
  explanation_error?: string | null;
  calendar?: Record<string, any> | null;
};

const apiBase = (import.meta.env.VITE_TIANJI_API_BASE || "").replace(/\/$/, "");

export async function executeLiuyao(input: {
  value: string;
  yao_values: number[];
}): Promise<ExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      domain: "liuyao",
      variant: "jingfang-eight-palaces-v1",
      input,
      explain: false,
      mode: "production",
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ExecuteResponse;
}


export async function executeBazi(input: {
  value: string;
}): Promise<ExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      domain: "bazi",
      variant: "ziping-structural-v1",
      input,
      explain: false,
      mode: "production",
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ExecuteResponse;
}


export type ScenarioExecuteResponse = {
  scenario_id: string;
  status: string;
  public_release: boolean;
  deterministic: boolean;
  result: Record<string, any>;
  rule_matches: Array<Record<string, any>>;
  trace: Array<Record<string, any>>;
  evidence: Record<string, Record<string, any>>;
  warnings: string[];
  limitations: string[];
};

export async function executeYearlyScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "yearly",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}


export async function executeRomanceScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "romance",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}


export async function executeCareerScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "career",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}


export async function executeLifeScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "life",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}


export async function executeDailyScenario(input: {
  birth_value: string;
  target_date: string;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "daily",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}


export async function executeWeeklyScenario(input: {
  birth_value: string;
  anchor_date: string;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "weekly",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}

export async function executeMonthlyScenario(input: {
  birth_value: string;
  target_month: string;
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "monthly",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}


export async function executeCompatibilityScenario(input: {
  person_a_birth_value: string;
  person_b_birth_value: string;
  person_a_traditional_role?: "male" | "female";
  person_b_traditional_role?: "male" | "female";
}): Promise<ScenarioExecuteResponse> {
  const response = await fetch(`${apiBase}/api/v1/scenarios/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: "compatibility",
      input,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail?.[0]?.msg ||
      data?.detail?.code ||
      `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as ScenarioExecuteResponse;
}

export type DreamCultureMatch = {
  scene: string;
  cultural_reading: string;
  short_quote: string;
  source_title: string;
  evidence_level: string;
};

export type DreamCultureResponse = {
  api_version: "v1";
  status: "reviewed_cultural_matches" | "no_reviewed_interpretation";
  public_release: true;
  cultural_reference_only: true;
  ai_enabled: false;
  personal_prediction: false;
  matches: DreamCultureMatch[];
  notice: string;
};

export async function lookupDreamCulture(dreamText: string): Promise<DreamCultureResponse> {
  const response = await fetch(`${apiBase}/api/v1/dream/culture`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ dream_text: dreamText }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      response.status === 503 ? "已审核梦象检索暂不可用，请稍后再试。" :
      response.status === 422 ? "请输入 2—500 字的梦境叙述。" :
      `查阅失败（HTTP ${response.status}）`
    );
  }
  if (data?.api_version !== "v1" || data?.public_release !== true ||
      data?.cultural_reference_only !== true || data?.ai_enabled !== false ||
      data?.personal_prediction !== false || !Array.isArray(data?.matches) ||
      !["reviewed_cultural_matches", "no_reviewed_interpretation"].includes(data?.status)) {
    throw new Error("服务端文化查阅合同不匹配，拒绝展示结果。");
  }
  return data as DreamCultureResponse;
}
