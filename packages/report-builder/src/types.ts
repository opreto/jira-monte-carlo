// Types for Sprint Radar report data
export interface SprintData {
  name: string
  startDate?: string
  endDate?: string
  completedPoints: number
  committedPoints: number
}

export interface VelocityMetrics {
  average: number
  median: number
  stdDev: number
  min: number
  max: number
  trend: number
}

export interface SimulationResult {
  percentiles: {
    [key: string]: number
  }
  dates?: {
    [key: string]: string
  }
}

export interface HealthScoreComponent {
  name: string
  score: number
  description: string
  insights?: string[]
  recommendations?: string[]
  detail_items?: Array<{
    key: string
    summary: string
    age_days: number
    status: string
    type: string
    assignee: string
  }>
}

export interface ProcessHealthMetrics {
  score: number
  wipScore: number
  sprintHealthScore: number
  flowEfficiencyScore: number
  leadTimeScore: number
  defectRateScore: number
  blockedItemsScore: number
  health_score_breakdown?: HealthScoreComponent[]
  aging_analysis?: any
  wip_analysis?: any
  sprint_health?: any
  blocked_items?: any
}

export interface ReportingCapabilities {
  available_reports: string[]
  all_reports: string[]
  unavailable_reports: { [key: string]: string[] }
  data_quality_score: number
}

export interface ReportData {
  projectName: string
  generatedAt: string
  remainingWork: number
  velocityMetrics: VelocityMetrics
  simulationResults: SimulationResult
  processHealth: ProcessHealthMetrics
  sprints: SprintData[]
  jql_query?: string
  jira_url?: string
  velocity_field?: string
  model_info?: {
    report_title?: string
    report_subtitle?: string
    methodology_description?: string
  }
  num_simulations?: number
  reporting_capabilities?: ReportingCapabilities
  charts?: {
    velocityTrend?: any
    burndown?: any
    monteCarloForecast?: any
    cycleTimeDistribution?: any
    cumulativeFlow?: any
    probability_distribution?: any
    forecast_timeline?: any
    confidence_intervals?: any
    story_size_breakdown?: any
    aging_distribution?: any
    aging_by_status?: any
    wip_by_status?: any
    sprint_completion_trend?: any
    sprint_scope_change?: any
    blocked_severity?: any
    health_score_gauge?: any
    health_score_breakdown?: any
  }
  summary_stats?: {
    [key: string]: {
      sprints: number
      date: string
      probability: string
      class: string
    }
  }
  jql_queries?: {
    forecast?: string
    history?: string
  }
  combinedScenarioData?: {
    baseline: ScenarioData
    adjusted: ScenarioData
    scenario: {
      description: string
      comparison: string
      adjustments: string[]
      team_changes: string[]
    }
    current_view: string
  }
  scenarioBanner?: string
  ml_decisions?: {
    decisions: Array<{
      decision_type: string
      method: string
      value: any
      model_name: string
      reasoning: string
      confidence?: number
      details?: any
    }>
  }
  scenarioCharts?: {
    baseline: {
      [key: string]: any
    }
    adjusted: {
      [key: string]: any
    }
  }
}

export interface ScenarioData {
  label: string
  percentiles: {
    p50: number
    p70: number
    p85: number
    p95: number
  }
  completion_sprints: number[]
  probability_distribution: Array<{
    sprint: number
    probability: number
  }>
  confidence_intervals: Array<{
    level: number
    lower: number
    upper: number
    value: number
  }>
  mean_completion: string | null
  std_dev_days: number
  summary_stats?: {
    [key: string]: {
      sprints: number
      date: string
      probability: string
      class: string
    }
  }
}