// Data contracts aligned with the future FastAPI backend.
// snake_case matches Pydantic; scores are 0..1; dates are ISO 8601 strings.

import { string } from "zod";
// 1. Define the core JSON types
export type JSONValue = string | number | boolean | null | JSONObject | JSONArray;
export type JSONObject = { [key: string]: JSONValue };
export type JSONArray = JSONValue[];

export type Priority = "Critical" | "High" | "Medium";

export type AlertStatus = "OPEN" | "ASSIGNED" | "RESOLVED" | "CLOSED";

export interface Alert {
  id: number;
  service: string;
  priority: Priority;
  final_score: number;
  status: AlertStatus;
  created_at: string;
}

export interface Ticket {
  id: number;
  alert_id: number;
  ticket_id: string
  service: string;
  priority: Priority;
  assignee: string;
  status: AlertStatus;
  created_at: string;
  updated_at: string;
  notification_sent: boolean;
  notification_time: string | null;
  incident_summary: JSONObject;
  resolution: string | null;
  preventive_action: string | null;
}


export interface WindowMetric {
  id: number;
  service: string;
  window_start: string;
  window_end: string;
  record_count: number;
  latency_mean: number;
  latency_max: number;
  cpu_mean: number;
  cpu_max: number;
  memory_mean: number;
  queue_lag_mean: number;
  queue_lag_max: number;
  error_count: number;
  ml_score: number;
  statistical_score: number;
  final_score: number;
  prediction: number;
  priority: Priority;
  ewma : number;
  cusum : number;
  persistence_score : number;
  incident_probability : number; 
  
}

export interface WindowMetricFull extends WindowMetric {
  payload_json?: Record<string, any>[] | Record<string, any> | null;
  payload_summary?: Record<string, any> | null;
}
export interface ServiceCount {
  service: string;
  count: number;
}
