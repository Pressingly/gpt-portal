<script lang="ts">
  import { filteredPlans, activeSubscription, modalState } from '../stores';
  import { getContext } from 'svelte';
  import PlanCard from './PlanCard.svelte';
  
  // Get i18n context
  const i18n = getContext('i18n');
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {#if $filteredPlans.length === 0}
    <div class="col-span-full text-center py-8">
      <p class="text-gray-600 dark:text-gray-400">
        {$i18n.t('No plans match your filter criteria')}
      </p>
    </div>
  {:else}
    {#each $filteredPlans as plan (plan.code)}
      <PlanCard {plan} />
    {/each}
  {/if}
</div>
