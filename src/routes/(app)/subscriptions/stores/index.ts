/**
 * Svelte stores for subscription plan management
 */

import { writable, derived } from 'svelte/store';
import type { Plan, Subscription, Usage } from './types';

// Store for all available plans
export const allPlans = writable<Plan[]>([]);
export const planLoadingStatus = writable<'idle' | 'loading' | 'success' | 'error'>('idle');
export const planError = writable<string | null>(null);

// Filter state
export const priceRange = writable<[number, number]>([0, 1000]);
export const sortOption = writable<'price-asc' | 'price-desc' | 'name-asc'>('price-asc');

// Derived store for filtered plans
export const filteredPlans = derived(
  [allPlans, priceRange, sortOption],
  ([$allPlans, $priceRange, $sortOption]) => {
    // Filter by price range
    let result = $allPlans.filter((plan: Plan) =>
      plan.amount_cents >= $priceRange[0] * 100 &&
      plan.amount_cents <= $priceRange[1] * 100
    );

    // Sort
    result = [...result].sort((a: Plan, b: Plan) => {
      if ($sortOption === 'price-asc') return a.amount_cents - b.amount_cents;
      if ($sortOption === 'price-desc') return b.amount_cents - a.amount_cents;
      return a.name.localeCompare(b.name);
    });

    return result;
  }
);

// Store for user subscription data
export const userSubscriptions = writable<Subscription[]>([]);
export const subscriptionLoadingStatus = writable<'idle' | 'loading' | 'success' | 'error'>('idle');
export const subscriptionError = writable<string | null>(null);

// Derived store for active subscription
export const activeSubscription = derived(
  userSubscriptions,
  ($userSubscriptions) => $userSubscriptions.find(sub => sub.status === 'active')
);

// Store for usage data
export const currentUsage = writable<Usage | null>(null);
export const usageLoadingStatus = writable<'idle' | 'loading' | 'success' | 'error'>('idle');
export const usageError = writable<string | null>(null);

// Store for UI state
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
