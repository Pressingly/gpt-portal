<script lang="ts">
  import { currentUsage, activeSubscription, usageLoadingStatus } from '../stores';
  import { getContext } from 'svelte';
  import Spinner from '$lib/components/common/Spinner.svelte';

  // Get i18n context
  const i18n = getContext('i18n');

  // Format date for display
  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  // Format price for display
  function formatPrice(amountCents: number, currency: string): string {
    const amount = amountCents / 100;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount);
  }

  // Calculate percentage for progress bar
  function calculatePercentage(used: number, total: number): number {
    if (total <= 0) return 0;
    const percentage = (used / total) * 100;
    return Math.min(percentage, 100); // Cap at 100%
  }
</script>

<div>
  {#if $usageLoadingStatus === 'loading'}
    <div class="flex justify-center py-4">
      <Spinner className="h-8 w-8" />
    </div>
  {:else if !$currentUsage}
    <div class="text-center py-4">
      <p class="text-gray-600 dark:text-gray-400">
        {$i18n.t('No usage data available')}
      </p>
    </div>
  {:else}
    <div class="space-y-6">
      <!-- Billing Period -->
      <div>
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {$i18n.t('Current Billing Period')}
        </h3>
        <p class="text-gray-600 dark:text-gray-400">
          {formatDate($currentUsage.from_datetime)} - {formatDate($currentUsage.to_datetime)}
        </p>
      </div>

      <!-- Total Usage -->
      <div>
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {$i18n.t('Total Usage')}
        </h3>
        <p class="text-lg font-bold text-gray-900 dark:text-white">
          {formatPrice($currentUsage.amount_cents, $currentUsage.currency)}
        </p>
      </div>

      <!-- Usage Breakdown -->
      {#if $currentUsage.charges_usage && $currentUsage.charges_usage.length > 0}
        <div>
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            {$i18n.t('Usage Breakdown')}
          </h3>
          <div class="space-y-4">
            {#each $currentUsage.charges_usage as charge}
              <div>
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    {charge.billable_metric.name}
                  </span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {charge.units} {$i18n.t('units')}
                  </span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-black dark:bg-opacity-50 rounded-full h-2.5">
                  <div
                    class="bg-blue-600 h-2.5 rounded-full"
                    style="width: {calculatePercentage(parseFloat(charge.units), 100)}%"
                  ></div>
                </div>
                <div class="flex justify-between items-center mt-1">
                  <span class="text-xs text-gray-500 dark:text-gray-400">
                    {formatPrice(charge.amount_cents, charge.amount_currency)}
                  </span>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>
