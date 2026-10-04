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
