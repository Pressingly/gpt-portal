# Subscription Utilities

This directory contains utility functions for working with subscription plans and pricing.

## Price Utilities

The `price-utils.ts` file provides functions for calculating and formatting subscription plan prices.

### `calculatePlanDisplayPrice`

This function calculates the display price for a subscription plan, handling both plans with a base price and pay-as-you-go plans like "Micro [beta]".

```typescript
function calculatePlanDisplayPrice(
  plan: Plan | null | undefined,
  formatAsCurrency: boolean = true,
  currency?: string
): string | number
```

#### Parameters:

- `plan`: The Plan object to calculate the price for
- `formatAsCurrency`: Whether to format the result as a currency string (default: true)
- `currency`: Optional currency code to use for formatting (defaults to plan's currency)

#### Returns:

- If `formatAsCurrency` is true: A formatted currency string (e.g., "$19.99")
- If `formatAsCurrency` is false: The raw price as a number (e.g., 19.99)

#### Behavior:

1. If the plan has a base price (`amount_cents` > 0), it uses that value
2. If the plan has no base price, it looks for the first charge with `billable_metric_code` equal to "credit_cents"
3. If no such charge is found, it checks for any charge with a price
4. If no price information is available, it defaults to 0

### `formatPrice`

A simple utility function to format a price in cents as a currency string.

```typescript
function formatPrice(amountCents: number, currency: string = 'USD'): string
```

#### Parameters:

- `amountCents`: The amount in cents
- `currency`: The currency code (e.g., 'USD')

#### Returns:

- A formatted currency string (e.g., "$19.99")

## Usage Examples

### Basic Usage

```typescript
import { calculatePlanDisplayPrice } from './utils/price-utils';
import type { Plan } from './stores/types';

// Get the formatted price for a plan
const formattedPrice = calculatePlanDisplayPrice(plan);
console.log(formattedPrice); // "$19.99"

// Get the raw price value
const rawPrice = calculatePlanDisplayPrice(plan, false);
console.log(rawPrice); // 19.99
```

### Component Usage

See the `PlanPriceDisplay.svelte` component for an example of how to use these utilities in a Svelte component.

```svelte
<PlanPriceDisplay plan={plan} size="large" />
```
