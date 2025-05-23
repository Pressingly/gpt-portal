<script lang="ts">
  import { onMount, getContext } from 'svelte';
  import {
    fetchAllPlans,
    fetchUserSubscriptions,
    fetchCurrentUsage
  } from '$lib/apis/lago';
  import Spinner from '$lib/components/common/Spinner.svelte';
  import { toast } from 'svelte-sonner';

  // Import components
  import PlanList from './components/PlanList.svelte';
  import PlanFilters from './components/PlanFilters.svelte';
  import SubscriptionModal from './components/SubscriptionModal.svelte';
  import UsageStats from './components/UsageStats.svelte';
  import SubscriptionHistory from './components/SubscriptionHistory.svelte';

  // Import stores
  import {
    allPlans,
    planLoadingStatus,
    planError,
    activeSubscription,
    subscriptionLoadingStatus,
    modalState,
    notification,
    userSubscriptions,
    currentUsage
  } from './stores';

  // Get i18n context
	const i18n = getContext('i18n');

  // State variables
  let loadingInitialData = true;

  onMount(async () => {
    try {
      // Set loading states
      planLoadingStatus.set('loading');
      subscriptionLoadingStatus.set('loading');

      // Load plans and subscriptions in parallel
      const [plansResponse, subscriptionsResponse] = await Promise.all([
        fetchAllPlans(),
        fetchUserSubscriptions()
      ]);

      // Update stores with the fetched data
      allPlans.set(plansResponse.plans || []);
      console.log('Plans response:', $allPlans);
      userSubscriptions.set(subscriptionsResponse.subscriptions || []);

      // Update loading states
      planLoadingStatus.set('success');
      subscriptionLoadingStatus.set('success');

      // If user has an active subscription, fetch usage data
      if ($activeSubscription) {
        try {
          const usageResponse = await fetchCurrentUsage($activeSubscription.external_id);
          currentUsage.set(usageResponse);
        } catch (error) {
          console.error('Error fetching usage data:', error);
          toast.error($i18n.t('Failed to load usage data'));
        }
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
      planLoadingStatus.set('error');
      subscriptionLoadingStatus.set('error');
      planError.set($i18n.t('Failed to load subscription data'));
      toast.error($i18n.t('Failed to load subscription data'));
    } finally {
      loadingInitialData = false;
    }
  });
</script>

<svelte:head>
  <title>{$i18n.t('Subscription Plans')}</title>
</svelte:head>

<div class="flex flex-col w-full h-full overflow-hidden bg-white dark:bg-gray-900">
  <!-- Header -->
  <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
    <h1 class="text-xl font-semibold text-gray-800 dark:text-white">
      {$i18n.t('Subscription Plans')}
    </h1>
  </div>

  <!-- Content -->
  <div class="flex-1 overflow-auto p-4">
    {#if loadingInitialData}
      <div class="flex flex-col items-center justify-center h-64">
        <Spinner className="h-8 w-8" />
        <p class="mt-4 text-gray-600 dark:text-gray-300">
          {$i18n.t('Loading subscription information...')}
        </p>
      </div>
    {:else}
      {#if $activeSubscription}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">
            {$i18n.t('Your Current Plan')}
          </h2>
          <UsageStats />
        </div>
      {/if}

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">
          {$i18n.t('Available Plans')}
        </h2>

        <PlanFilters />

        {#if $planLoadingStatus === 'loading'}
          <div class="flex justify-center py-8">
            <Spinner className="h-8 w-8" />
          </div>
        {:else if $planLoadingStatus === 'error'}
          <div class="text-center py-8">
            <p class="text-red-500 dark:text-red-400">
              {$planError || $i18n.t('Failed to load plans')}
            </p>
            <button
              class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              on:click={() => window.location.reload()}
            >
              {$i18n.t('Try Again')}
            </button>
          </div>
        {:else if $allPlans.length === 0}
          <div class="text-center py-8">
            <p class="text-gray-600 dark:text-gray-400">
              {$i18n.t('No subscription plans available')}
            </p>
          </div>
        {:else}
          <PlanList />
        {/if}
      </div>

      {#if $activeSubscription}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">
            {$i18n.t('Subscription History')}
          </h2>
          <SubscriptionHistory />
        </div>
      {/if}
    {/if}
  </div>
</div>

{#if $modalState.isOpen}
  <SubscriptionModal />
{/if}

{#if $notification.show}
  <div class="fixed bottom-4 right-4 z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 max-w-md">
      <div class="flex items-center">
        {#if $notification.type === 'success'}
          <svg class="w-6 h-6 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        {:else if $notification.type === 'error'}
          <svg class="w-6 h-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        {:else}
          <svg class="w-6 h-6 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        {/if}
        <p class="text-gray-800 dark:text-white">{$notification.message}</p>
      </div>
      <button
        class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        on:click={() => notification.set({ ...$notification, show: false })}
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
  </div>
{/if}
