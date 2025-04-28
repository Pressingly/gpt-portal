/**
 * Model information types for displaying model costs and benefits
 */

/**
 * Pricing information for a model
 */
export interface ModelPricing {
  /** Cost per million input tokens in USD */
  inputTokens: number;
  /** Cost per million output tokens in USD */
  outputTokens: number;
  /** Optional price per 1,000 requests (for models like Perplexity) */
  requestPrice?: number;
}

/**
 * Model tier classification
 */
export type ModelTier = 'Standard' | 'Value' | 'Pro';

/**
 * Detailed information about a model
 */
export interface ModelInfo {
  /** Company that created the model */
  company: string;
  /** Tier classification (Standard, Value, Pro) */
  tier: ModelTier;
  /** Full model name */
  modelName: string;
  /** Pricing information */
  pricing: ModelPricing;
  /** Description of best use cases */
  bestUseCases: string;
  /** Optional additional capabilities or features */
  additionalInfo?: string;
}

/**
 * Map of model IDs to their detailed information
 */
export interface ModelInfoMap {
  [modelId: string]: ModelInfo;
}
