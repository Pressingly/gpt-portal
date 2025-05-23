/**
 * Type definitions for Lago API data models
 */

export interface PlanFeature {
  code: string;
  name: string;
  description: string;
  value_numeric?: number;
  value_string?: string;
}

export interface PlanCharge {
  lago_id: string;
  lago_billable_metric_id: string;
  billable_metric_code: string;
  charge_model: string; // 'standard', 'package', 'graduated', etc.
  invoice_display_name: string;
  min_amount_cents: number;
  properties: any; // Varies based on charge_model
  filters: any[];
}

export interface Plan {
  lago_id: string;
  code: string;
  name: string;
  invoice_display_name?: string;
  description: string;
  amount_cents: number;
  amount_currency: string;
  trial_period: number;
  pay_in_advance: boolean;
  interval: string; // 'monthly', 'yearly', etc.
  created_at: string;
  charges: PlanCharge[];
  taxes: any[];
  minimum_commitment?: any;
  usage_thresholds?: any[];
}

export interface Subscription {
  lago_id: string;
  external_id: string;
  lago_customer_id: string;
  external_customer_id: string;
  billing_time: string;
  name: string;
  plan_code: string;
  status: 'active' | 'pending' | 'terminated' | 'canceled';
  created_at: string;
  canceled_at?: string;
  started_at: string;
  ending_at?: string;
  subscription_at: string;
  terminated_at?: string;
  previous_plan_code?: string;
  next_plan_code?: string;
  downgrade_plan_date?: string;
  trial_ended_at?: string;
  current_billing_period_started_at: string;
  current_billing_period_ending_at: string;
  plan?: Plan;
}

export interface ChargeUsage {
  units: string;
  events_count: number;
  amount_cents: number;
  amount_currency: string;
  charge: {
    lago_id: string;
    charge_model: string;
    invoice_display_name: string;
  };
  billable_metric: {
    lago_id: string;
    name: string;
    code: string;
    aggregation_type: string;
  };
  filters: any[];
  grouped_usage: any[];
}

export interface Usage {
  from_datetime: string;
  to_datetime: string;
  issuing_date: string;
  lago_invoice_id?: string;
  currency: string;
  amount_cents: number;
  taxes_amount_cents: number;
  total_amount_cents: number;
  charges_usage: ChargeUsage[];
}
