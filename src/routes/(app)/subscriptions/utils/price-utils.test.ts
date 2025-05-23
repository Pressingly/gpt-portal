/**
 * Tests for price utility functions
 * 
 * This file demonstrates how to use the calculatePlanDisplayPrice function
 * with different types of Plan objects.
 */

import { calculatePlanDisplayPrice, formatPrice } from './price-utils';
import type { Plan } from '../stores/types';

// Example 1: Plan with a base price
const planWithBasePrice: Plan = {
  lago_id: 'plan_123',
  code: 'standard',
  name: 'Standard Plan',
  description: 'Standard subscription plan',
  amount_cents: 1999, // $19.99
  amount_currency: 'USD',
  trial_period: 14,
  pay_in_advance: true,
  interval: 'monthly',
  created_at: '2023-01-01T00:00:00Z',
  charges: [],
  taxes: []
};

// Example 2: Pay-as-you-go plan with credit_cents charge (like "Micro [beta]")
const microBetaPlan: Plan = {
  lago_id: 'plan_456',
  code: 'micro-beta',
  name: 'Micro [beta]',
  description: 'Pay-as-you-go subscription plan',
  amount_cents: 0, // No base price
  amount_currency: 'USD',
  trial_period: 0,
  pay_in_advance: false,
  interval: 'monthly',
  created_at: '2023-01-01T00:00:00Z',
  charges: [
    {
      lago_id: 'charge_123',
      lago_billable_metric_id: 'metric_123',
      billable_metric_code: 'credit_cents',
      charge_model: 'package',
      invoice_display_name: 'Credits Used',
      min_amount_cents: 0,
      properties: {
        amount: '0.2', // $0.20 per package
        free_units: 1,
        package_size: 10
      },
      filters: []
    }
  ],
  taxes: []
};

// Example 3: Plan with no price information
const planWithNoPrice: Plan = {
  lago_id: 'plan_789',
  code: 'free',
  name: 'Free Plan',
  description: 'Free subscription plan',
  amount_cents: 0,
  amount_currency: 'USD',
  trial_period: 0,
  pay_in_advance: false,
  interval: 'monthly',
  created_at: '2023-01-01T00:00:00Z',
  charges: [],
  taxes: []
};

// Example usage
console.log('Standard Plan Price:', calculatePlanDisplayPrice(planWithBasePrice)); // "$19.99"
console.log('Micro [beta] Plan Price:', calculatePlanDisplayPrice(microBetaPlan)); // "$0.20"
console.log('Free Plan Price:', calculatePlanDisplayPrice(planWithNoPrice)); // "$0.00"

// Get raw price values
console.log('Standard Plan Raw Price:', calculatePlanDisplayPrice(planWithBasePrice, false)); // 19.99
console.log('Micro [beta] Plan Raw Price:', calculatePlanDisplayPrice(microBetaPlan, false)); // 0.2

// Format with different currency
console.log('Standard Plan in EUR:', calculatePlanDisplayPrice(planWithBasePrice, true, 'EUR')); // "€19.99"

// Using the formatPrice utility
console.log('Formatted price from cents:', formatPrice(1999)); // "$19.99"
console.log('Formatted price in EUR:', formatPrice(1999, 'EUR')); // "€19.99"
