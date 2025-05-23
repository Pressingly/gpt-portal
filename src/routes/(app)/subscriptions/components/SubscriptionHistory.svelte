<script lang="ts">
  import { userSubscriptions } from '../stores';
  import { getContext, onMount } from 'svelte';
  import { fetchCustomerInvoices } from '$lib/apis/lago';
  import Spinner from '$lib/components/common/Spinner.svelte';
  
  // Get i18n context
  const i18n = getContext('i18n');
  
  // State variables
  let invoices = [];
  let loadingInvoices = true;
  let error = null;
  
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
  
  // Format subscription status
  function formatStatus(status: string): string {
    switch (status) {
      case 'active':
        return $i18n.t('Active');
      case 'pending':
        return $i18n.t('Pending');
      case 'terminated':
        return $i18n.t('Terminated');
      case 'canceled':
        return $i18n.t('Canceled');
      default:
        return status;
    }
  }
  
  // Get status color class
  function getStatusColorClass(status: string): string {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'terminated':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'canceled':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  }
  
  // Load invoices on mount
  onMount(async () => {
    try {
      loadingInvoices = true;
      const response = await fetchCustomerInvoices();
      invoices = response.invoices || [];
    } catch (err) {
      console.error('Error fetching invoices:', err);
      error = $i18n.t('Failed to load invoice history');
    } finally {
      loadingInvoices = false;
    }
  });
</script>

<div>
  <!-- Subscription History -->
  <div class="mb-6">
    <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
      {$i18n.t('Subscription History')}
    </h3>
    
    {#if $userSubscriptions.length === 0}
      <p class="text-gray-600 dark:text-gray-400 py-2">
        {$i18n.t('No subscription history available')}
      </p>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Plan')}
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Status')}
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Started')}
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Ended')}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {#each $userSubscriptions as subscription}
              <tr>
                <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {subscription.plan_code}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getStatusColorClass(subscription.status)}">
                    {formatStatus(subscription.status)}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {formatDate(subscription.subscription_at)}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {subscription.terminated_at ? formatDate(subscription.terminated_at) : '-'}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
  
  <!-- Invoice History -->
  <div>
    <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
      {$i18n.t('Invoice History')}
    </h3>
    
    {#if loadingInvoices}
      <div class="flex justify-center py-4">
        <Spinner className="h-8 w-8" />
      </div>
    {:else if error}
      <p class="text-red-500 dark:text-red-400 py-2">
        {error}
      </p>
    {:else if invoices.length === 0}
      <p class="text-gray-600 dark:text-gray-400 py-2">
        {$i18n.t('No invoice history available')}
      </p>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Invoice')}
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Date')}
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Amount')}
              </th>
              <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {$i18n.t('Status')}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {#each invoices as invoice}
              <tr>
                <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {invoice.number}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {formatDate(invoice.issuing_date)}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {formatPrice(invoice.total_amount_cents, invoice.currency)}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                    {invoice.status}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>
