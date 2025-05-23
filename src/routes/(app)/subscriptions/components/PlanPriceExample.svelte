<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchAllPlans } from '$lib/apis/lago';
  import PlanPriceDisplay from './PlanPriceDisplay.svelte';
  import type { Plan } from '../stores/types';

  // State
  let plans: Plan[] = [];
  let loading = true;
  let error: string | null = null;

  // Fetch plans on component mount
  onMount(async () => {
    try {
      const response = await fetchAllPlans();
      plans = response.plans || [];
      loading = false;
    } catch (err) {
      console.error('Error fetching plans:', err);
      error = 'Failed to load subscription plans';
      loading = false;
    }
  });
</script>

<div class="p-4 bg-white dark:bg-black dark:bg-opacity-50 rounded-lg shadow">
  <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Plan Pricing Example</h2>

  {#if loading}
    <p class="text-gray-600 dark:text-gray-400">Loading plans...</p>
  {:else if error}
    <p class="text-red-500">{error}</p>
  {:else if plans.length === 0}
    <p class="text-gray-600 dark:text-gray-400">No plans available</p>
  {:else}
    <div class="space-y-4">
      {#each plans as plan}
        <div class="border border-gray-200 dark:border-gray-700 p-3 rounded bg-white dark:bg-black dark:bg-opacity-50">
          <h3 class="font-medium text-gray-800 dark:text-white">{plan.name}</h3>
          <div class="flex justify-between items-center mt-2">
            <span class="text-sm text-gray-600 dark:text-gray-400">Price:</span>
            <PlanPriceDisplay {plan} size="medium" />
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
