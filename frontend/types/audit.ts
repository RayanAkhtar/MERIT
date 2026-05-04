/**
 * Core types for the Recruitment Intelligence Audit Trail.
 * Used for Bayesian Evidence Fusion and Temporal Analysis visualization.
 */

export interface SourceDetail {
  source: string;
  score: number;
  explanation: string;
  trust?: number;
  derivation?: string;
  is_semantic_bridge?: boolean;
}

export interface TemporalParams {
  lambda: number;
  delta_t: number;
  weight: number;
}

export interface AuditItem {
  sources: string[];
  item?: string;
  component?: string;
  score: number;
  weight?: number;
  notes?: string;
  influence?: number;
  alpha?: number;
  beta?: number;
  uncertainty?: number;
  confidence_label?: string;
  confidence_reason?: string;
  temporal_formula?: boolean;
  temporal_params?: TemporalParams;
  source_details?: SourceDetail[];
  impact_attribution?: Record<string, number>;
}

export interface WeightedAverageBreakdown {
  name: string;
  score: number;
  weight: number;
}

export interface StuffingAudit {
  term: string;
  count: number;
  density: string;
  limit: number;
  penalty_per: number;
}

export interface CandidateDetail {
  name?: string;
  email?: string;
  phone?: string;
  cv_url: string;
  cv_experience?: any[];
  cv_education?: any[];
  projects_history?: any[];
  github_profile?: any;
  github_projects?: any[];
  linkedin_profile?: any;
  linkedin_experience?: any[];
  linkedin_projects?: any[];
  linkedin_certifications?: any[];
  linkedin_volunteering?: any[];
  metrics: MetricAudit[];
}

export interface MetricAudit {
  name: string;
  score: number;
  weight?: number;
  formula?: string;
  technical_formula?: string;
  integrity_penalty_applied?: boolean;
  integrity_penalty_value?: number;
  integrity_audit_details?: StuffingAudit;
  improvements?: (string | { text: string; variables: string[] })[];
  weighted_sum?: number;
  total_weight?: number;
  weighted_average_breakdown?: WeightedAverageBreakdown[];
  breakdown?: AuditItem[];
}
