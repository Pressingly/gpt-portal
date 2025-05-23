/**
 * Utility functions for subscription plan pricing
 */

import type { Plan } from '../stores/types';

/**
 * Calculates the display price for a subscription plan
 * 
 * @param plan The Plan object to calculate the price for
 * @param formatAsCurrency Whether to format the result as a currency string (default: true)
 * @param currency Optional currency code to use for formatting (defaults to plan's currency)
 * @returns The formatted price as a string or the raw price as a number if formatAsCurrency is false
 */
export function calculatePlanDisplayPrice(
  plan: Plan | null | undefined,
  formatAsCurrency: boolean = true,
  currency?: string
): string | number {
  if (!plan) {
    return formatAsCurrency ? '$0.00' : 0;
  }

  let price: number;

  // If the plan has a base price, use that
  if (plan.amount_cents > 0) {
    price = plan.amount_cents / 100; // Convert cents to dollars
  } 
  // Otherwise, look for the first charge with billable_metric_code "credit_cents"
  else {
    const creditCharge = plan.charges?.find(charge => 
      charge.billable_metric_code === 'credit_cents'
    );

    // If we found a credit charge, use its amount property
    if (creditCharge && creditCharge.properties && creditCharge.properties.amount) {
      // The amount is already in dollars, so no need to divide by 100
      price = parseFloat(creditCharge.properties.amount);
    } 
    // If no credit charge is found, check for any charge
    else if (plan.charges && plan.charges.length > 0 && plan.charges[0].properties?.amount) {
      price = parseFloat(plan.charges[0].properties.amount);
    } 
    // Default to 0 if no price information is available
    else {
      price = 0;
    }
  }

  // Return the raw price if formatting is not requested
  if (!formatAsCurrency) {
    return price;
  }

  // Format the price as currency
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || plan.amount_currency || 'USD',
    minimumFractionDigits: 2
  }).format(price);
}

/**
 * Formats a price in cents as a currency string
 * 
 * @param amountCents The amount in cents
 * @param currency The currency code (e.g., 'USD')
 * @returns Formatted currency string
 */
export function formatPrice(amountCents: number, currency: string = 'USD'): string {
  const amount = amountCents / 100;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2
  }).format(amount);
}
