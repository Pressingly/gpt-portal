/**
 * Utility functions for calculating query costs based on token usage and model pricing
 */

import { get } from 'svelte/store';
import { models } from '$lib/stores';

// Default pricing if model-specific pricing is not available
const DEFAULT_PRICING = {
  input: 0.0000015,  // $0.0000015 per input token
  output: 0.000002   // $0.000002 per output token
};

/**
 * Calculate the cost of a query based on token usage and model pricing
 * @param modelId The ID of the model used
 * @param inputTokens Number of input tokens
 * @param outputTokens Number of output tokens
 * @returns The calculated cost in USD
 */
export function calculateQueryCost(
  modelId: string,
  inputTokens: number,
  outputTokens: number
): number {
  // Get the current models from the store
  const currentModels = get(models);
  
  // Find the model in the store
  const model = currentModels.find(m => m.id === modelId);
  
  // Get pricing information (either from the model or use defaults)
  const inputPrice = model?.pricing?.input || DEFAULT_PRICING.input;
  const outputPrice = model?.pricing?.output || DEFAULT_PRICING.output;
  
  // Calculate cost
  const inputCost = inputTokens * inputPrice;
  const outputCost = outputTokens * outputPrice;
  
  return inputCost + outputCost;
}

/**
 * Calculate the cost for multiple models (for multi-LLM queries)
 * @param modelIds Array of model IDs used in the query
 * @param inputTokens Number of input tokens
 * @param outputTokens Number of output tokens
 * @returns The calculated cost in USD
 */
export function calculateMultiModelQueryCost(
  modelIds: string[],
  inputTokens: number,
  outputTokens: number
): number {
  // If there's only one model, use the single model calculation
  if (modelIds.length === 1) {
    return calculateQueryCost(modelIds[0], inputTokens, outputTokens);
  }
  
  // For multiple models, calculate the average cost
  // This is a simplified approach - in a real implementation, you might
  // want to distribute tokens among models or use a more complex formula
  let totalCost = 0;
  
  for (const modelId of modelIds) {
    totalCost += calculateQueryCost(modelId, inputTokens / modelIds.length, outputTokens / modelIds.length);
  }
  
  return totalCost;
}
