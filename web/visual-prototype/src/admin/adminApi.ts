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


export type AdminRuleBinding = {
  id: string;
  domain: string;
  name: string;
  variant: string;
  execution_status: string;
  validation_status: string;
  golden_case_ids: string[];
  evidence_scope: string;
};

export type AdminRuleRecord = {
  id: string;
  domain: string;
  name: string;
  execution_status: string;
  school: string;
  variant: string;
  difference: string;
  exceptions: string[];
  confidence: string;
  phase2_bindings: AdminRuleBinding[];
  evidence: AdminConflictEvidence[];
};

export type AdminEvidenceRecord = {
  id: string;
  domain: string;
  name: string;
  classic_id: string;
  classic_title: string;
  chapter_id: string;
  chapter_title: string;
  source_id: string;
  locator: string;
  original_text: string;
  evidence_level: string;
  source_url: string;
  commit: string;
  review: {
    status: string;
    method: string;
    scope: string;
  };
  used_by_entity_ids: string[];
  phase2_rule_ids: string[];
};

async function fetchProtectedRecords<T>(path: string, token: string): Promise<T[]> {
  const response = await fetch(`${apiBase}${path}`, {
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
  return Array.isArray(data?.records) ? (data.records as T[]) : [];
}

export function fetchAdminRules(token: string): Promise<AdminRuleRecord[]> {
  return fetchProtectedRecords<AdminRuleRecord>("/api/v1/admin/governance/rules", token);
}

export function fetchAdminEvidence(token: string): Promise<AdminEvidenceRecord[]> {
  return fetchProtectedRecords<AdminEvidenceRecord>("/api/v1/admin/governance/evidence", token);
}


export type AdminClassicChapter = {
  id: string;
  name: string;
  locator: string;
  reviewed_section_count: number;
  section_ids: string[];
};

export type AdminClassicRecord = {
  id: string;
  domain: string;
  name: string;
  body_stage: string;
  source_id: string;
  source_title: string;
  evidence_level: string;
  source_url: string;
  commit: string;
  rights_basis: string;
  review_scope: string;
  chapter_count: number;
  reviewed_section_count: number;
  phase2_rule_ids: string[];
  chapters: AdminClassicChapter[];
};

export function fetchAdminClassics(token: string): Promise<AdminClassicRecord[]> {
  return fetchProtectedRecords<AdminClassicRecord>("/api/v1/admin/governance/classics", token);
}


export type AdminChapterRecord = {
  id: string;
  domain: string;
  name: string;
  locator: string;
  classic_id: string;
  classic_title: string;
  body_stage: string;
  source_id: string;
  source_title: string;
  evidence_level: string;
  source_url: string;
  commit: string;
  rights_basis: string;
  review_scope: string;
  reviewed_section_count: number;
  section_ids: string[];
  used_by_entity_ids: string[];
  phase2_rule_ids: string[];
};

export function fetchAdminChapters(token: string): Promise<AdminChapterRecord[]> {
  return fetchProtectedRecords<AdminChapterRecord>("/api/v1/admin/governance/chapters", token);
}
