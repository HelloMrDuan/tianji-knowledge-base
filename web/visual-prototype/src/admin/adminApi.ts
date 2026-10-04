const apiBase = (import.meta.env.VITE_TIANJI_API_BASE || "").replace(/\/$/, "");

export type AdminConflictEvidence = {
  source_id: string;
  section_id: string;
  classic_id: string;
  classic_title: string;
  chapter_id: string;
  chapter_title: string;
  locator: string;
  original_text: string;
  evidence_level: string;
  source_url: string;
  commit: string;
};

export type AdminConflictPosition = {
  id: string;
  label: string;
  position: string;
  section_ids: string[];
};

export type AdminConflictRecord = {
  id: string;
  domain: string;
  name: string;
  kind: string;
  status: string;
  dimension: string;
  positions: AdminConflictPosition[];
  production_policy: string;
  executable_policy: string;
  confidence: string;
  evidence: AdminConflictEvidence[];
};

export type AdminConflictResponse = {
  api_version: string;
  read_only: boolean;
  public_release: boolean;
  records: AdminConflictRecord[];
};

export async function fetchAdminConflicts(token: string): Promise<AdminConflictResponse> {
  const response = await fetch(`${apiBase}/api/v1/admin/governance/conflicts`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const code = data?.detail?.code;
    const message =
      code === "admin_auth_not_configured"
        ? "服务端尚未配置后台只读令牌。"
        : code === "admin_unauthorized"
          ? "后台访问令牌无效。"
          : data?.detail?.message || `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }
  return data as AdminConflictResponse;
}
