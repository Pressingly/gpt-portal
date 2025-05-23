<script lang="ts">
  import { activeSubscription, modalState } from '../stores';
  import { getContext } from 'svelte';
  import type { Plan } from '../stores/types';
  import { calculatePlanDisplayPrice, formatPrice } from '../utils/price-utils';

  // Get i18n context
  const i18n = getContext('i18n');
  // Props
  export let plan: Plan;

  // Determine if this plan is the user's current plan
  $: isCurrentPlan = $activeSubscription && $activeSubscription.plan_code === plan.code;

  // Format interval for display
  function formatInterval(interval: string): string {
    switch (interval) {
      case 'monthly':
        return $i18n.t('per month');
      case 'yearly':
        return $i18n.t('per year');
      case 'weekly':
        return $i18n.t('per week');
      case 'quarterly':
        return $i18n.t('per quarter');
      default:
        return interval;
    }
  }

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

<div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4 shadow-sm h-full flex flex-col relative">
  {#if isCurrentPlan}
    <div class="absolute top-0 right-0 transform translate-x-2 -translate-y-2">
      <span class="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full">
        {$i18n.t('Current')}
      </span>
    </div>
  {/if}

  <h3 class="text-lg font-semibold text-gray-800 dark:text-white mb-2">{plan.name}</h3>

  <p class="text-gray-600 dark:text-gray-300 mb-4 flex-grow">
    {plan.description || $i18n.t('No description available')}
  </p>

  <div class="mb-4">
    <div class="flex justify-between items-center mb-2">
      <span class="text-lg font-bold text-gray-900 dark:text-white">
        {calculatePlanDisplayPrice(plan)}
      </span>
      <span class="text-sm text-gray-500 dark:text-gray-400">
        {formatInterval(plan.interval)}
      </span>
    </div>

    {#if plan.charges && plan.charges.length > 0}
      <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {$i18n.t('Usage Charges')}
        </h4>
        <ul class="space-y-1">
          {#each plan.charges as charge}
            <li class="text-sm flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">{charge.billable_metric_code}</span>
              <span class="text-gray-800 dark:text-gray-200">
                {#if charge.charge_model === 'standard'}
                  {formatPrice(parseFloat(charge.properties.amount) * 100, plan.amount_currency)} {$i18n.t('per unit')}
                {:else if charge.charge_model === 'package'}
                  {formatPrice(parseFloat(charge.properties.amount) * 100, plan.amount_currency)} {$i18n.t('per')} {charge.properties.package_size} {$i18n.t('units')}
                {:else if charge.charge_model === 'graduated'}
                  {$i18n.t('Tiered pricing')}
                {:else}
                  {charge.charge_model}
                {/if}
              </span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>

  <div class="mt-auto">
    {#if isCurrentPlan}
      <button
        class="w-full py-2 px-4 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        on:click={handleUnsubscribe}
      >
        {$i18n.t('Unsubscribe')}
      </button>
    {:else}
      <button
        class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        on:click={handleSubscribe}
      >
        {$i18n.t('Subscribe')}
      </button>
    {/if}
  </div>
</div>
