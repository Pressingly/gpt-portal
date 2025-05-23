# Technical Design: Custom Subscription Plan UI with Lago API Integration

## Overview

This document outlines the technical design for replacing the iframe-based subscription page with a custom-built Svelte UI that directly integrates with the Lago API. The implementation will provide a comprehensive view of subscription plans, user subscription status, and usage statistics.

## Architecture

### Component Structure

```
src/routes/(app)/subscriptions/
├── +page.svelte                 # Main subscription page container
├── components/
│   ├── PlanList.svelte          # Container for all plan cards
│   ├── PlanCard.svelte          # Individual plan display
│   ├── PlanFilters.svelte       # Filter and sort controls
│   ├── SubscriptionModal.svelte # Confirmation modal
│   ├── UsageStats.svelte        # Usage statistics component
│   ├── SubscriptionHistory.svelte # Subscription history view
│   ├── PriceDisplay.svelte      # Formatted price display
│   └── FeatureList.svelte       # List of plan features with icons
└── stores/
    ├── plans.ts                 # Store for plan data
    ├── subscriptions.ts         # Store for subscription data
    ├── usage.ts                 # Store for usage data
    └── ui.ts                    # Store for UI state
```

### Data Models

#### Plan Model
```typescript
interface PlanFeature {
  code: string;
  name: string;
  description: string;
  value_numeric?: number;
  value_string?: string;
}

interface PlanCharge {
  lago_id: string;
  lago_billable_metric_id: string;
  billable_metric_code: string;
  charge_model: string; // 'standard', 'package', 'graduated', etc.
  invoice_display_name: string;
  min_amount_cents: number;
  properties: any; // Varies based on charge_model
  filters: any[];
}

interface Plan {
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
```

#### Subscription Model
```typescript
interface Subscription {
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
```

#### Usage Model
```typescript
interface ChargeUsage {
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

interface Usage {
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
```

## API Integration

### Lago API Endpoints

1. **Plans Endpoints**
   - `GET /plans` - Retrieve all available plans
     - Optional query parameters: `page`, `per_page`
     - Returns a list of plan objects

2. **Subscriptions Endpoints**
   - `GET /subscriptions` - List all subscriptions
     - Optional query parameters: `page`, `per_page`, `external_customer_id`, `plan_code`, `status[]`
     - Returns a list of subscription objects
   - `POST /subscriptions` - Create a subscription
     - Required parameters in request body: `external_customer_id`, `plan_code`
     - Returns the created subscription object
   - `DELETE /subscriptions/{external_id}` - Terminate a subscription
     - Path parameter: `external_id`
     - Optional query parameter: `status`
     - Returns the terminated subscription object

3. **Customer Usage Endpoints**
   - `GET /customers/{external_customer_id}/current_usage` - Get current usage
     - Required query parameter: `external_subscription_id`
     - Optional query parameter: `apply_taxes`
     - Returns detailed usage information for the current billing period

### API Service Implementation

```typescript
// lagoApi.ts - Service for Lago API interactions
import { user } from '$lib/stores';
import { get } from 'svelte/store';

const LAGO_API_URL = 'https://gpt-portal-lagoapi.sandbox.pressingly.net/api/v1';

// Helper function for API requests
async function lagoApiRequest(endpoint: string, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${import.meta.env.VITE_LAGO_API_KEY}`
    }
  };

  const response = await fetch(`${LAGO_API_URL}${endpoint}`, {
    ...defaultOptions,
    ...options
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'An error occurred');
  }

  return response.json();
}

// Plans
export async function fetchAllPlans() {
  return lagoApiRequest('/plans');
}

// Subscriptions
export async function fetchUserSubscriptions(userId: string) {
  return lagoApiRequest(`/subscriptions?external_customer_id=${userId}`);
}

export async function createSubscription(userId: string, planCode: string, options = {}) {
  const payload = {
    subscription: {
      external_customer_id: userId,
      plan_code: planCode,
      billing_time: "anniversary",
      ...options
    }
  };

  return lagoApiRequest('/subscriptions', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function cancelSubscription(subscriptionId: string, status?: string) {
  const queryParams = status ? `?status=${status}` : '';
  return lagoApiRequest(`/subscriptions/${subscriptionId}${queryParams}`, {
    method: 'DELETE'
  });
}

// Usage
export async function fetchCurrentUsage(userId: string, subscriptionId: string) {
  return lagoApiRequest(
    `/customers/${userId}/current_usage?external_subscription_id=${subscriptionId}`
  );
}
```

## State Management with Svelte Stores

```typescript
// plans.ts - Store for plan data
import { writable, derived } from 'svelte/store';

export const allPlans = writable<Plan[]>([]);
export const planLoadingStatus = writable<'idle' | 'loading' | 'success' | 'error'>('idle');
export const planError = writable<string | null>(null);

// Filter state
export const priceRange = writable<[number, number]>([0, 1000]);
export const selectedFeatures = writable<string[]>([]);
export const sortOption = writable<'price-asc' | 'price-desc' | 'name-asc'>('price-asc');

// Derived store for filtered plans
export const filteredPlans = derived(
  [allPlans, priceRange, selectedFeatures, sortOption],
  ([$allPlans, $priceRange, $selectedFeatures, $sortOption]) => {
    // Filter and sort logic
    // ...
    return filteredResults;
  }
);

// subscriptions.ts - Store for user subscription data
export const userSubscriptions = writable<Subscription[]>([]);
export const subscriptionLoadingStatus = writable<'idle' | 'loading' | 'success' | 'error'>('idle');
export const subscriptionError = writable<string | null>(null);

// Derived store for active subscription
export const activeSubscription = derived(
  userSubscriptions,
  ($userSubscriptions) => $userSubscriptions.find(sub => sub.status === 'active')
);

// usage.ts - Store for usage data
export const currentUsage = writable<Usage | null>(null);
export const usageLoadingStatus = writable<'idle' | 'loading' | 'success' | 'error'>('idle');
export const usageError = writable<string | null>(null);

// ui.ts - Store for UI state
export const modalState = writable<{
  isOpen: boolean;
  type: 'subscribe' | 'unsubscribe' | null;
  planCode: string | null;
}>({
  isOpen: false,
  type: null,
  planCode: null
});

export const notification = writable<{
  show: boolean;
  type: 'success' | 'error' | 'info';
  message: string;
}>({
  show: false,
  type: 'info',
  message: ''
});
```

## Error Handling Strategy

### API Error Handling
```typescript
// Error handling in API calls
try {
  const response = await lagoApiRequest('/plans');
  allPlans.set(response.plans);
  planLoadingStatus.set('success');
} catch (error) {
  planError.set(error.message);
  planLoadingStatus.set('error');

  // Show error notification
  notification.set({
    show: true,
    type: 'error',
    message: `Failed to load plans: ${error.message}`
  });
}
```

### UI Error States
1. **Loading States**: Show loading spinners or skeleton loaders during API calls
2. **Error Messages**: Display user-friendly error messages with retry options
3. **Empty States**: Handle cases where no plans or subscriptions are available
4. **Fallback UI**: Provide simplified UI when certain features fail to load

### Edge Cases to Consider
1. **No Active Subscription**: Handle UI when user has no active subscription
2. **API Unavailability**: Implement retry logic and fallback UI
3. **Plan Changes**: Handle transitions between subscription states
4. **Concurrent Operations**: Prevent multiple subscription operations at once
5. **Network Issues**: Detect offline status and provide appropriate messaging
6. **Authorization Failures**: Handle expired tokens or permission issues
7. **Data Inconsistencies**: Validate data from API before displaying

## Responsive Design Considerations

### Breakpoints
```css
/* Mobile first approach */
/* Base styles for mobile (up to 640px) */

/* Small tablets and large phones (640px and up) */
@media (min-width: 640px) {
  /* Small tablet styles */
}

/* Tablets and small laptops (768px and up) */
@media (min-width: 768px) {
  /* Tablet styles */
}

/* Laptops and desktops (1024px and up) */
@media (min-width: 1024px) {
  /* Desktop styles */
}

/* Large screens (1280px and up) */
@media (min-width: 1280px) {
  /* Large screen styles */
}
```

### Layout Adjustments
1. **Mobile View**:
   - Single column layout
   - Stacked plan cards
   - Simplified filters with dropdown menus
   - Collapsible sections for usage details

2. **Tablet View**:
   - Two-column grid for plan cards
   - Side-by-side layout for filters and sorting
   - Expanded usage statistics

3. **Desktop View**:
   - Three or four-column grid for plan cards
   - Full feature set visible
   - Detailed usage statistics with charts

### Touch Considerations
- Minimum touch target size of 44×44 pixels
- Adequate spacing between interactive elements
- Swipe gestures for plan navigation on mobile
- Touch-friendly filters and controls

## Accessibility Requirements

### Semantic HTML
- Use proper heading hierarchy (h1, h2, h3)
- Use semantic elements (button, nav, section) instead of generic divs
- Implement proper form labels and controls

### ARIA Attributes
```html
<!-- Example of accessible plan card -->
<div
  role="region"
  aria-labelledby="plan-title-123"
  class="plan-card {isCurrentPlan ? 'current-plan' : ''}"
>
  {#if isCurrentPlan}
    <div class="current-plan-badge" aria-hidden="true">Current Plan</div>
    <span class="sr-only">This is your current plan</span>
  {/if}

  <h3 id="plan-title-123">{plan.name}</h3>
  <!-- Plan content -->

  <button
    aria-pressed={isCurrentPlan}
    aria-label={isCurrentPlan ? `Unsubscribe from ${plan.name} plan` : `Subscribe to ${plan.name} plan`}
    class="btn {isCurrentPlan ? 'btn-outline' : 'btn-primary'}"
  >
    {isCurrentPlan ? 'Unsubscribe' : 'Subscribe'}
  </button>
</div>
```

### Keyboard Navigation
- Ensure all interactive elements are focusable
- Implement logical tab order
- Add focus styles that are visible in all color schemes
- Support keyboard shortcuts for common actions

### Screen Reader Support
- Test with screen readers (NVDA, VoiceOver)
- Add alt text to all images
- Ensure dynamic content changes are announced
- Use aria-live regions for important updates

### Color and Contrast
- Ensure sufficient contrast between text and background
- Don't rely solely on color to convey information
- Support dark mode with appropriate contrast ratios
- Test with color blindness simulators

## Implementation Phases

### Phase 1: Core Structure and API Integration
1. Set up project structure and component files
2. Implement data models and Svelte stores
3. Create Lago API service with basic endpoints
4. Implement main subscription page layout
5. Create basic PlanList component with minimal styling

**Dependencies**: None

### Phase 2: Plan Display and Subscription Management
1. Implement PlanCard component with detailed information
2. Create subscription modal for confirmation flows
3. Implement subscribe/unsubscribe functionality
4. Add loading states and basic error handling
5. Implement current plan indicator

**Dependencies**: Phase 1

### Phase 3: Usage Statistics and History
1. Implement UsageStats component
2. Create SubscriptionHistory view
3. Add detailed usage information and charts
4. Implement invoice history display
5. Add usage-based recommendations

**Dependencies**: Phase 2

### Phase 4: Filtering, Sorting, and UI Enhancements
1. Implement PlanFilters component
2. Add sorting functionality
3. Create responsive layouts for all screen sizes
4. Implement accessibility features
5. Add animations and transitions

**Dependencies**: Phase 3

### Phase 5: Polish and Optimization
1. Implement comprehensive error handling
2. Add edge case handling
3. Optimize performance
4. Implement caching strategies
5. Add final UI polish and refinements

**Dependencies**: Phase 4

## Conclusion

This technical design provides a comprehensive roadmap for implementing a custom subscription plan UI with direct Lago API integration. By following the phased approach, developers can incrementally build and test the functionality while ensuring a high-quality user experience.

The implementation prioritizes:
- Direct integration with Lago API
- Comprehensive plan and subscription management
- Detailed usage statistics
- Responsive design for all devices
- Accessibility compliance
- Error handling and edge cases

This design serves as a complete guide that any developer can follow to implement the custom subscription plan UI.

## Appendix: Component Implementation Examples

### Main Subscription Page (+page.svelte)

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import {
    fetchAllPlans,
    fetchUserSubscriptions,
    fetchCurrentUsage
  } from '$lib/services/lagoApi';
  import {
    filteredPlans,
    planLoadingStatus,
    planError,
    activeSubscription,
    subscriptionLoadingStatus,
    subscriptionError,
    modalState,
    notification
  } from '$lib/stores';
  import { user } from '$lib/stores';
  import PlanFilters from './components/PlanFilters.svelte';
  import PlanList from './components/PlanList.svelte';
  import SubscriptionModal from './components/SubscriptionModal.svelte';
  import SubscriptionHistory from './components/SubscriptionHistory.svelte';
  import UsageStats from './components/UsageStats.svelte';
  import LoadingSpinner from '$lib/components/common/LoadingSpinner.svelte';
  import ErrorMessage from '$lib/components/common/ErrorMessage.svelte';
  import SuccessNotification from '$lib/components/common/SuccessNotification.svelte';

  let loadingInitialData = true;

  onMount(async () => {
    try {
      // Load plans and subscriptions in parallel
      await Promise.all([
        fetchAllPlans(),
        fetchUserSubscriptions($user.id)
      ]);

      // If user has an active subscription, fetch usage data
      if ($activeSubscription) {
        await fetchCurrentUsage($user.id, $activeSubscription.external_id);
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      loadingInitialData = false;
    }
  });
</script>

<div class="subscription-page">
  <h1>Subscription Plans</h1>

  {#if loadingInitialData}
    <div class="loading-container">
      <LoadingSpinner />
      <p>Loading subscription information...</p>
    </div>
  {:else}
    {#if $activeSubscription}
      <div class="current-subscription">
        <h2>Your Current Plan</h2>
        <UsageStats />
      </div>
    {/if}

    <div class="plans-section">
      <h2>Available Plans</h2>
      <PlanFilters />

      {#if $planLoadingStatus === 'loading'}
        <LoadingSpinner />
      {:else if $planLoadingStatus === 'error'}
        <ErrorMessage message={$planError} />
      {:else}
        <PlanList plans={$filteredPlans} />
      {/if}
    </div>

    {#if $activeSubscription}
      <div class="history-section">
        <h2>Subscription History</h2>
        <SubscriptionHistory />
      </div>
    {/if}
  {/if}

  {#if $modalState.isOpen}
    <SubscriptionModal />
  {/if}

  {#if $notification.show}
    <SuccessNotification
      type={$notification.type}
      message={$notification.message}
    />
  {/if}
</div>

<style>
  .subscription-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
    color: var(--color-text-primary);
  }

  h2 {
    font-size: 1.5rem;
    margin: 1.5rem 0 1rem;
    color: var(--color-text-primary);
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
  }

  .current-subscription,
  .plans-section,
  .history-section {
    background: var(--color-bg-card);
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  @media (max-width: 768px) {
    .subscription-page {
      padding: 1rem 0.5rem;
    }

    h1 {
      font-size: 1.75rem;
    }

    h2 {
      font-size: 1.25rem;
    }

    .current-subscription,
    .plans-section,
    .history-section {
      padding: 1rem;
    }
  }
</style>
```

### PlanCard Component

```svelte
<script lang="ts">
  import { createSubscription, cancelSubscription } from '$lib/services/lagoApi';
  import { activeSubscription, modalState } from '$lib/stores';
  import PriceDisplay from './PriceDisplay.svelte';
  import FeatureList from './FeatureList.svelte';

  export let plan;

  // Determine if this plan is the user's current plan
  $: isCurrentPlan = $activeSubscription && $activeSubscription.plan_code === plan.code;

  // Handle subscribe button click
  function handleSubscribe() {
    modalState.set({
      isOpen: true,
      type: 'subscribe',
      planCode: plan.code
    });
  }

  // Handle unsubscribe button click
  function handleUnsubscribe() {
    modalState.set({
      isOpen: true,
      type: 'unsubscribe',
      planCode: plan.code
    });
  }
</script>

<div
  role="region"
  aria-labelledby="plan-title-{plan.lago_id}"
  class="plan-card {isCurrentPlan ? 'current-plan' : ''}"
>
  {#if isCurrentPlan}
    <div class="current-plan-badge" aria-hidden="true">Current Plan</div>
    <span class="sr-only">This is your current plan</span>
  {/if}

  <div class="plan-header">
    <h3 id="plan-title-{plan.lago_id}">{plan.name}</h3>
    <p class="plan-description">{plan.description}</p>
  </div>

  <div class="plan-price">
    <PriceDisplay
      amount={plan.amount_cents}
      currency={plan.amount_currency}
      interval={plan.interval}
    />
  </div>

  <div class="plan-features">
    <h4>Features</h4>
    <FeatureList features={plan.features} />
  </div>

  <div class="plan-charges">
    <h4>Usage Charges</h4>
    {#each plan.charges as charge}
      <div class="charge-item">
        <span class="charge-name">{charge.billable_metric_code}</span>
        <span class="charge-amount">
          {#if charge.charge_model === 'standard'}
            ${charge.properties.amount} per unit
          {:else if charge.charge_model === 'package'}
            ${charge.properties.amount} per {charge.properties.package_size} units
          {:else if charge.charge_model === 'graduated'}
            Tiered pricing
          {/if}
        </span>
      </div>
    {/each}
  </div>

  <div class="plan-action">
    <button
      aria-pressed={isCurrentPlan}
      aria-label={isCurrentPlan ? `Unsubscribe from ${plan.name} plan` : `Subscribe to ${plan.name} plan`}
      class="btn {isCurrentPlan ? 'btn-outline' : 'btn-primary'}"
      on:click={isCurrentPlan ? handleUnsubscribe : handleSubscribe}
    >
      {isCurrentPlan ? 'Unsubscribe' : 'Subscribe'}
    </button>
  </div>
</div>

<style>
  .plan-card {
    background: var(--color-bg-card);
    border-radius: 0.5rem;
    padding: 1.5rem;
    position: relative;
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--color-border);
  }

  .plan-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  }

  .current-plan {
    border: 2px solid var(--color-primary);
    box-shadow: 0 5px 15px rgba(var(--color-primary-rgb), 0.2);
  }

  .current-plan-badge {
    position: absolute;
    top: -10px;
    right: 10px;
    background: var(--color-primary);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }

  /* Additional styles omitted for brevity */
</style>
```

## Implementation Notes and Recommendations

### Development Environment Setup

1. **Environment Variables**
   - Create a `.env` file with the following variables:
     ```
     VITE_LAGO_API_URL=https://gpt-portal-lagoapi.sandbox.pressingly.net/api/v1
     VITE_LAGO_API_KEY=your_lago_api_key
     ```
   - Ensure these variables are properly loaded in the Svelte configuration

2. **TypeScript Configuration**
   - Update `tsconfig.json` to include strict type checking
   - Add type definitions for Lago API responses

3. **Component Library Integration**
   - Consider using existing UI components from the application's design system
   - Ensure consistent styling with the rest of the application

### Testing Strategy

1. **Unit Tests**
   - Test individual components in isolation
   - Mock API responses for consistent testing
   - Test edge cases (empty plans, API errors, etc.)

2. **Integration Tests**
   - Test the complete subscription flow
   - Verify API integration with mock server
   - Test responsive design across different screen sizes

3. **End-to-End Tests**
   - Test the complete user journey
   - Verify subscription creation and cancellation
   - Test with real API endpoints in a staging environment

### Performance Considerations

1. **API Caching**
   - Implement caching for plan data to reduce API calls
   - Use local storage for non-sensitive data
   - Implement proper cache invalidation strategies

2. **Lazy Loading**
   - Lazy load components not visible in the viewport
   - Implement code splitting for large components
   - Defer loading of non-critical resources

3. **Optimistic UI Updates**
   - Update UI immediately before API calls complete
   - Revert changes if API calls fail
   - Show loading indicators only for long operations

### Deployment Considerations

1. **Feature Flags**
   - Implement feature flags to control rollout
   - Allow gradual migration from iframe to custom UI
   - Enable easy rollback if issues arise

2. **Analytics**
   - Add tracking for subscription events
   - Monitor user engagement with the new UI
   - Track conversion rates and subscription changes

3. **Documentation**
   - Document API integration details
   - Create user guides for the new subscription UI
   - Document troubleshooting steps for common issues

By following these recommendations, the implementation will be robust, maintainable, and provide a seamless user experience.
