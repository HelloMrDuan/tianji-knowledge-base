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

type JsonObject = Record<string, unknown>;
function isRecord(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

const INVALID_RESPONSE = "服务端返回数据不完整，暂不能展示测算结果，请稍后重试。";
function invalidResponse(): never {
  throw new ApiError("invalid", INVALID_RESPONSE);
}

/** No raw upstream technical messages are displayed without a conservative safe-text check. */
function safeServerMessage(input: unknown): string | null {
  if (typeof input !== "string") return null;
  const message = input.trim();
  // No control characters, markup, path fragments or backend diagnostics.
  if (!message || message.length > 120 || /[\r\n\t<>\x00-\x1f]/.test(message)) return null;
  if (/(https?:\/\/|www\.|[a-z]:[\\/]|\/(?:api|home|var|src)\/|\.py\b|\.ts\b|\.js\b|trace|stack|rule[_\s-]?id|evidence[_\s-]?id|token|exception|keyerror|internal|file\s|line\s?\d|\bsha\b|数据库堆栈|内部路径|规则编号)/i.test(message)) return null;
  return message;
}
function userMessageFor(status: number, detail: unknown): string {
  const parsed = isRecord(detail) ? detail : null;
  const first = Array.isArray(detail) ? detail[0] : null;
  // Custom Chinese business messages from the reviewed API are preferable to generic status text.
  const custom = safeServerMessage(parsed?.message) ?? safeServerMessage(isRecord(first) ? first.msg : null);
  if (custom) return custom;
  if (status === 400 || status === 422) return "输入内容有误，请检查后重试。";
  if (status === 503) return "服务暂时繁忙，请稍后重试。";
  if (status >= 500) return "服务端出现问题，请稍后重试。";
  return "请求失败，请稍后重试。";
}

function assertExecuteResponse(data: unknown, domain: string): ExecuteResponse {
  if (!isRecord(data) || data.domain !== domain || data.deterministic !== true ||
      !isRecord(data.chart) || !isRecord(data.evidence) ||
      !Array.isArray(data.rule_matches) || !Array.isArray(data.trace) ||
      !Array.isArray(data.warnings) || !Array.isArray(data.limitations)) invalidResponse();
  return data as ExecuteResponse;
}

/**
 * The eight user-facing STRUCTURE-ONLY scenarios deliberately remain
 * production_limited / public_release:false in the reviewed Scenario Engine.
 * Their public projection API is usable, but this is NOT approval to promote
 * unrestricted fortune claims. Validate the precise limited contract.
 */
const LIMITED_SCOPES: Record<string, string> = {
  daily: "daily_structure_only",
  weekly: "weekly_structure_only",
  monthly: "monthly_structure_only",
  yearly: "annual_structure_only",
  romance: "xianchi_structure_only",
  career: "career_wealth_structure_only",
  compatibility: "two_person_structure_only",
  life: "deterministic_aggregate_only",
};

function assertScenarioResponse(data: unknown, scenarioId: string): ScenarioExecuteResponse {
  if (!isRecord(data) || data.scenario_id !== scenarioId ||
      data.deterministic !== true || !isRecord(data.result) ||
      !isRecord(data.evidence) || !Array.isArray(data.rule_matches) ||
      !Array.isArray(data.trace) || !Array.isArray(data.warnings) ||
      !Array.isArray(data.limitations)) invalidResponse();
  const scope = LIMITED_SCOPES[scenarioId];
  if (!scope) invalidResponse();
  // Existing controlled-HTTP browser fixtures model a positive published scenario,
  // but authentic production returns the narrower reviewed structural contract.
  const limited = data.public_release === false &&
      data.status === "production_limited" && data.result.release_scope === scope;
  const published = data.public_release === true &&
      ["production", "success"].includes(String(data.status));
  if (!limited && !published) invalidResponse();
  return data as ScenarioExecuteResponse;
}

async function requestJson(path: string, body: unknown): Promise<unknown> {
  const controller = new AbortController();
  // Hold the deadline through response BODY consumption, not only HTTP headers.
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    const response = await fetch(`${apiBase}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    let data: unknown;
    try {
      const content = await response.text();
      data = content ? JSON.parse(content) : null;
    } catch (err) {
      if (controller.signal.aborted) throw new ApiError("timeout", "请求超时，请检查网络后重试。");
      if (!response.ok) throw new ApiError("server", userMessageFor(response.status, null), response.status);
      throw new ApiError("invalid", "服务端返回数据格式异常，请稍后重试。");
    }
    if (!response.ok) {
      throw new ApiError("server", userMessageFor(response.status, isRecord(data) ? data.detail : null), response.status);
    }
    if (!isRecord(data)) invalidResponse();
    return data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (controller.signal.aborted || (err instanceof Error && err.name === "AbortError")) {
      throw new ApiError("timeout", "请求超时，请检查网络后重试。");
    }
    throw new ApiError("network", "网络连接失败，请检查网络后重试。");
  } finally {
    clearTimeout(timer);
  }
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
  return assertExecuteResponse(data, "liuyao");
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
  return assertExecuteResponse(data, "bazi");
}

/** B012 / TJ-030.1: real public execution for Yijing structure (no verdict). */
export async function executeYijing(input: {
  bits: string;
  changing_lines: number[];
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
    domain: "yijing",
    variant: "bottom-up-six-lines-v1",
    input,
    explain: false,
    mode: "production",
  });
  return assertExecuteResponse(data, "yijing");
}

/** B012 / TJ-030.4: real public execution for Liuren structure (no verdict). */
export async function executeLiuren(input: {
  value: string;
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
    domain: "liuren",
    variant: "daquan-nine-methods-lodged-stems-v1",
    input,
    explain: false,
    mode: "production",
  });
  return assertExecuteResponse(data, "liuren");
}

/** B014 / TJ-030.2: real public execution for Ziwei structure (no verdict).
 * Leap lunar months are rejected by the backend (non-leap lunar only);
 * no dayun, brightness, or fortune verdict is computed. */
export async function executeZiwei(input: {
  value: string;
  year_boundary: "lunar-new-year";
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
    domain: "ziwei",
    variant: "quanshu-lunar-iztro-mutagen-v1",
    input,
    explain: false,
    mode: "production",
  });
  return assertExecuteResponse(data, "ziwei");
}

/** B014 / TJ-030.3: real public execution for Qimen structure (no verdict).
 * Fixed qfdk rotating-plate scope only; super-intercalation (超接置闰),
 * hidden stems, and pattern verdicts are NOT computed. */
export async function executeQimen(input: {
  value: string;
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
    domain: "qimen",
    variant: "qfdk-exact-term-midnight-v2",
    input,
    explain: false,
    mode: "production",
  });
  return assertExecuteResponse(data, "qimen");
}

/** B014 / TJ-030.5: real public execution for Fengshui structure (no verdict).
 * Production mode only: compass mountains and facing are computed, but the
 * absolute period is refused without an explicit research epoch. */
export async function executeFengshui(input: {
  degrees: number;
}): Promise<ExecuteResponse> {
  const data = await requestJson("/api/v1/public/execute", {
    domain: "fengshui",
    variant: "compass-half-open-explicit-epoch-v1",
    input,
    explain: false,
    mode: "production",
  });
  return assertExecuteResponse(data, "fengshui");
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
  return assertScenarioResponse(data, "yearly");
}


export async function executeRomanceScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "romance",
      input,
  });
  return assertScenarioResponse(data, "romance");
}


export async function executeCareerScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "career",
      input,
  });
  return assertScenarioResponse(data, "career");
}


export async function executeLifeScenario(input: {
  birth_value: string;
  target_year: number;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "life",
      input,
  });
  return assertScenarioResponse(data, "life");
}


export async function executeDailyScenario(input: {
  birth_value: string;
  target_date: string;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "daily",
      input,
  });
  return assertScenarioResponse(data, "daily");
}


export async function executeWeeklyScenario(input: {
  birth_value: string;
  anchor_date: string;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "weekly",
      input,
  });
  return assertScenarioResponse(data, "weekly");
}

export async function executeMonthlyScenario(input: {
  birth_value: string;
  target_month: string;
}): Promise<ScenarioExecuteResponse> {
  const data = await requestJson("/api/v1/scenarios/public", {
      scenario_id: "monthly",
      input,
  });
  return assertScenarioResponse(data, "monthly");
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
  return assertScenarioResponse(data, "compatibility");
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
