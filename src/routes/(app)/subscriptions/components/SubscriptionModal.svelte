<script lang="ts">
  import { modalState, allPlans, activeSubscription, userSubscriptions } from '../stores';
  import { getContext } from 'svelte';
  import {
    createSubscription,
    cancelSubscription,
    fetchUserSubscriptions
  } from '$lib/apis/lago';

  // Get i18n context
  const i18n = getContext('i18n');

  // State variables
  let processingSubscription = false;
  let errorMessage = '';

  // Get the current plan details
  $: currentPlan = $modalState.planCode
    ? $allPlans.find(plan => plan.code === $modalState.planCode)
    : null;

  // Function to handle subscription creation
  async function handleSubscribe() {
    if (!$modalState.planCode || processingSubscription) return;

    try {
      processingSubscription = true;
      errorMessage = '';

      // Create subscription
      await createSubscription($modalState.planCode);

      // Refresh subscriptions
      const subscriptionsResponse = await fetchUserSubscriptions();
      userSubscriptions.set(subscriptionsResponse.subscriptions || []);

      // Close modal
      modalState.set({ isOpen: false, type: null, planCode: null });

    } catch (error) {
      console.error('Error creating subscription:', error);
      errorMessage = $i18n.t('Failed to subscribe to plan. Please try again.');
    } finally {
      processingSubscription = false;
    }
  }

  // Function to handle subscription cancellation
  async function handleUnsubscribe() {
    if (!$activeSubscription || processingSubscription) return;

    try {
      processingSubscription = true;
      errorMessage = '';

      // Cancel subscription
      await cancelSubscription($activeSubscription.external_id);

      // Refresh subscriptions
      const subscriptionsResponse = await fetchUserSubscriptions();
      userSubscriptions.set(subscriptionsResponse.subscriptions || []);

      // Close modal
      modalState.set({ isOpen: false, type: null, planCode: null });

    } catch (error) {
      console.error('Error canceling subscription:', error);
      errorMessage = $i18n.t('Failed to unsubscribe from plan. Please try again.');
    } finally {
      processingSubscription = false;
    }
  }

  // Function to handle modal action button click
  function handleModalAction() {
    if ($modalState.type === 'subscribe') {
      handleSubscribe();
    } else if ($modalState.type === 'unsubscribe') {
      handleUnsubscribe();
    }
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
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-md w-full">
    <div class="flex justify-between items-start mb-4">
      <h2 class="text-xl font-semibold text-gray-800 dark:text-white">
        {$modalState.type === 'subscribe' ? $i18n.t('Subscribe to Plan') : $i18n.t('Unsubscribe from Plan')}
      </h2>
      <button
        class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        on:click={() => modalState.set({ isOpen: false, type: null, planCode: null })}
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    {#if currentPlan && $modalState.type === 'subscribe'}
      <div class="mb-6">
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
          <h3 class="font-medium text-gray-800 dark:text-white mb-2">{currentPlan.name}</h3>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-2">{currentPlan.description}</p>
          <div class="flex justify-between items-center">
            <span class="font-bold text-gray-900 dark:text-white">
              {formatPrice(currentPlan.amount_cents, currentPlan.amount_currency)}
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {formatInterval(currentPlan.interval)}
            </span>
          </div>
        </div>

        <p class="text-gray-600 dark:text-gray-300 mb-4">
          {$i18n.t('Are you sure you want to subscribe to this plan? You will be charged immediately.')}
        </p>
      </div>
    {:else if $modalState.type === 'unsubscribe'}
      <div class="mb-6">
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          {$i18n.t('Are you sure you want to unsubscribe from your current plan? You will lose access to the plan benefits at the end of your billing period.')}
        </p>
      </div>
    {/if}

    {#if errorMessage}
      <div class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-md mb-4">
        {errorMessage}
      </div>
    {/if}

    <div class="flex justify-end space-x-4">
      <button
        class="px-4 py-2 bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        on:click={() => modalState.set({ isOpen: false, type: null, planCode: null })}
        disabled={processingSubscription}
      >
        {$i18n.t('Cancel')}
      </button>

      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center"
        on:click={handleModalAction}
        disabled={processingSubscription}
      >
        {#if processingSubscription}
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {$i18n.t('Processing...')}
        {:else}
          {$modalState.type === 'subscribe' ? $i18n.t('Subscribe') : $i18n.t('Unsubscribe')}
        {/if}
      </button>
    </div>
  </div>
</div>
