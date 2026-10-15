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

/**
 * TJ-007.4 任务A：统一请求执行与错误处理
 * - 30秒超时（AbortController）
 * - 错误分类：网络/超时/服务端/数据格式
 * - 用户友好的中文提示，不泄漏技术细节
 */
export const API_TIMEOUT_MS = 30000;

export class ApiError extends Error {
  kind: "network" | "timeout" | "server" | "invalid";
  status?: number;
  constructor(kind: ApiError["kind"], message: string, status?: number) {
    super(message);
    this.kind = kind;
    this.status = status;
  }
}

function userMessageFor(status: number, detail: any): string {
  if (status === 400 || status === 422) {
    const msg = detail?.message || detail?.[0]?.msg;
    if (typeof msg === "string" && msg.length > 0 && msg.length < 200) return msg;
    return "输入内容有误，请检查后重试。";
  }
  if (status === 503) return "服务暂时繁忙，请稍后重试。";
  if (status >= 500) return "服务端出现问题，请稍后重试。";
  return "请求失败，请稍后重试。";
}

async function requestJson(path: string, body: unknown): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  let response: Response;
  try {
    response = await fetch(`${apiBase}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timer);
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("timeout", "请求超时，请检查网络后重试。");
    }
    throw new ApiError("network", "网络连接失败，请检查网络后重试。");
  }
  clearTimeout(timer);

  let data: any = {};
  try {
    const text = await response.text();
    data = text ? JSON.parse(text) : {};
  } catch {
    throw new ApiError("invalid", "服务端返回数据格式异常，请稍后重试。", response.status);
  }

  if (!response.ok) {
    throw new ApiError("server", userMessageFor(response.status, data?.detail), response.status);
  }
  return data;
}

export async function executeLiuyao(input: {
  value: string;
  yao_values: number[];
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
    domain: "liuyao",
    variant: "jingfang-eight-palaces-v1",
    input,
    explain: false,
    mode: "production",
  });
  return data as ExecuteResponse;
}


export async function executeBazi(input: {
  value: string;
  strength_variant?: "ditiansui-root-visibility-v1";
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
      domain: "bazi",
      variant: "ziping-structural-v1",
      input,
      explain: false,
      mode: "production",
  });
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
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "yearly",
      input,
  });
  return data as ScenarioExecuteResponse;
}


export async function executeRomanceScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "romance",
      input,
  });
  return data as ScenarioExecuteResponse;
}


export async function executeCareerScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "career",
      input,
  });
  return data as ScenarioExecuteResponse;
}


export async function executeLifeScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "life",
      input,
  });
  return data as ScenarioExecuteResponse;
}


export async function executeDailyScenario(input: {
  birth_value: string;
  target_date: string;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "daily",
      input,
  });
  return data as ScenarioExecuteResponse;
}


export async function executeWeeklyScenario(input: {
  birth_value: string;
  anchor_date: string;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "weekly",
      input,
  });
  return data as ScenarioExecuteResponse;
}

export async function executeMonthlyScenario(input: {
  birth_value: string;
  target_month: string;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "monthly",
      input,
  });
  return data as ScenarioExecuteResponse;
}


export async function executeCompatibilityScenario(input: {
  person_a_birth_value: string;
  person_b_birth_value: string;
  person_a_traditional_role?: "male" | "female";
  person_b_traditional_role?: "male" | "female";
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "compatibility",
      input,
  });
  return data as ScenarioExecuteResponse;
}

export type DreamCultureMatch = {
  scene: string;
  matched_texts: string[];
  cultural_reading: string;
  short_quote: string;
  source_title: string;
  evidence_level: string;
};

export type DreamUnreviewedTopic = {
  label: "考试" | "怀孕" | "结婚" | "工作" | "被追" | "故人" | "死亡";
  matched_texts: string[];
};

export type DreamCultureResponse = {
  api_version: "v1";
  status: "reviewed_cultural_matches" | "no_reviewed_interpretation";
  public_release: true;
  cultural_reference_only: true;
  ai_enabled: false;
  personal_prediction: false;
  matches: DreamCultureMatch[];
  unreviewed_topics: DreamUnreviewedTopic[];
  notice: string;
};

export async function lookupDreamCulture(dreamText: string): Promise<DreamCultureResponse> {
  let data: any;
  try {
    data = await requestJson("/api/v1/dream/culture", { dream_text: dreamText });
  } catch (err) {
    // 保留原有的友好提示
    if (err instanceof ApiError && err.status === 422) {
      throw new ApiError("server", "请输入 2—500 字的梦境叙述。", 422);
    }
    throw err;
  }
  if (data?.api_version !== "v1" || data?.public_release !== true ||
      data?.cultural_reference_only !== true || data?.ai_enabled !== false ||
      data?.personal_prediction !== false || !Array.isArray(data?.matches) ||
      !Array.isArray(data?.unreviewed_topics) ||
      !data.unreviewed_topics.every((item: unknown) => {
        if (!item || typeof item !== "object") return false;
        const topic = item as DreamUnreviewedTopic;
        return ["考试", "怀孕", "结婚", "工作", "被追", "故人", "死亡"].includes(topic.label) &&
          Array.isArray(topic.matched_texts) &&
          topic.matched_texts.length > 0 &&
          topic.matched_texts.every((s) => typeof s === "string" && s.length > 0);
      }) ||
      !["reviewed_cultural_matches", "no_reviewed_interpretation"].includes(data?.status)) {
    throw new ApiError("invalid", "服务端文化查阅合同不匹配，拒绝展示结果。");
  }
  return data as DreamCultureResponse;
}
