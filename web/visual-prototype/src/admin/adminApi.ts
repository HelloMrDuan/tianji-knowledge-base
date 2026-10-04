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


export type AdminTermEvidence = {
  source_id: string;
  section_id: string;
  classic_id: string;
  classic_title: string;
  chapter_id: string;
  chapter_title: string;
  locator: string;
  evidence_level: string;
};

export type AdminTermRecord = {
  id: string;
  domain: string;
  name: string;
  aliases: string[];
  definition: string;
  confidence: string;
  definition_kind: string;
  production_interpretation: boolean | null;
  related_terms: string[];
  related_rule_ids: string[];
  phase2_rule_ids: string[];
  evidence: AdminTermEvidence[];
};

export function fetchAdminTerms(token: string): Promise<AdminTermRecord[]> {
  return fetchProtectedRecords<AdminTermRecord>("/api/v1/admin/governance/terms", token);
}


export type AdminSourceRecord = {
  id: string;
  title: string;
  author: string | null;
  era: string | null;
  repository: string | null;
  url: string;
  commit: string;
  license: string | null;
  public_domain: boolean | null;
  retrieved_at: string | null;
  evidence_level: string;
  kind: string;
  rights_basis: string;
  review_scope: string;
  domains: string[];
  classic_ids: string[];
  chapter_ids: string[];
  section_count: number;
  entity_count: number;
};

export function fetchAdminSources(token: string): Promise<AdminSourceRecord[]> {
  return fetchProtectedRecords<AdminSourceRecord>("/api/v1/admin/governance/sources", token);
}


export type AdminLayerRecord = {
  id: "raw" | "quarantine" | "canonical";
  name: string;
  tracked_file_count: number;
  classic_count: number;
  entity_count: number;
  domain_count: number;
  domains: string[];
  protected_file_count: number;
  registered_ingestion_sources: number;
  ingestion_modes: Record<string, number>;
  production_queryable: boolean;
  promotion_policy: string;
  release_policy: string;
};

export function fetchAdminLayers(token: string): Promise<AdminLayerRecord[]> {
  return fetchProtectedRecords<AdminLayerRecord>("/api/v1/admin/governance/layers", token);
}


export type AdminAlgorithmRecord = {
  id: string;
  domain: string;
  variant: string;
  provider: string;
  scope: string;
  unresolved: string[];
  rule_count: number;
  executable_rule_count: number;
  validated_rule_count: number;
  golden_case_ids: string[];
  phase1_rule_ids: string[];
  production_ready: boolean;
  deterministic: boolean;
  ai_may_compute_chart: boolean;
};

export function fetchAdminAlgorithms(token: string): Promise<AdminAlgorithmRecord[]> {
  return fetchProtectedRecords<AdminAlgorithmRecord>("/api/v1/admin/governance/algorithms", token);
}


export type AdminProviderRecord = {
  id: string;
  driver: string;
  allowed_drivers: string[];
  status: "disabled" | "incomplete" | "invalid" | "configured";
  configured: boolean;
  endpoint_origin: string;
  endpoint_host: string;
  model: string;
  api_key_present: boolean;
  api_key_exposed: false;
  timeout_seconds: number | null;
  max_output_tokens: number | null;
  prompt_version: string;
  live_connectivity_verified: false;
  automatic_release_allowed: false;
};

export function fetchAdminProvider(token: string): Promise<AdminProviderRecord[]> {
  return fetchProtectedRecords<AdminProviderRecord>("/api/v1/admin/system/provider", token);
}


export type AdminPromptRecord = {
  id: string;
  version: string;
  sha256: string;
  instruction: string;
  instruction_length: number;
  selected: boolean;
  configured_selection: string;
  selection_registered: boolean;
  default: boolean;
  production_eligible: boolean;
  immutable: boolean;
  automatic_release_allowed: false;
};

export function fetchAdminPrompts(token: string): Promise<AdminPromptRecord[]> {
  return fetchProtectedRecords<AdminPromptRecord>("/api/v1/admin/system/prompts", token);
}


export type AdminEvaluationRecord = {
  id: string;
  domain: string;
  suite_id: string;
  variants: string[];
  eval_case_count: number;
  explanation_case_count: number;
  refusal_control_count: number;
  suite_golden_ref_count: number;
  phase2_golden_count: number;
  phase2_golden_ids: string[];
  eval_case_ids: string[];
  tag_counts: Record<string, number>;
  engine_baseline_main_sha: string;
  engine_baseline_file_count: number;
  fixed_suite: true;
  tracked_status: "fixture_only";
  live_model_quality_verified: false;
  human_semantic_review_required: true;
  automatic_release_allowed: false;
  online_ready: false;
};

export function fetchAdminEvaluations(token: string): Promise<AdminEvaluationRecord[]> {
  return fetchProtectedRecords<AdminEvaluationRecord>("/api/v1/admin/system/evaluations", token);
}
