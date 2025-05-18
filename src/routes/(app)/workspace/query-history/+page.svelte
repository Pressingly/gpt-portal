<script lang="ts">
  import { onMount } from 'svelte';
  import { getQueryHistory, type QueryHistoryItem } from '$lib/apis/query_history';
  import { getToken } from '$lib/utils/auth';
  import { page } from '$app/stores';

  let history: QueryHistoryItem[] = [];
  let loading = true;
  let error = '';
  let currentPage = 1;
  let pageSize = 8;
  let totalPages = 1;
  let remainingBalance = 'Loading...';

  function formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZoneName: 'short'
      }).format(date);
    } catch (e) {
      console.error('Error formatting timestamp:', e);
      return timestamp;
    }
  }

  async function fetchHistory() {
    loading = true;
    error = '';
    try {
      const token = await getToken();
      console.log('Got token:', token ? 'Token exists' : 'No token');
      const data = await getQueryHistory(token, currentPage, pageSize);
      console.log('Query history response:', data);
      history = data.items;
      totalPages = data.total_pages;
    } catch (e) {
      console.error('Error fetching history:', e);
      error = e.message || 'Unknown error';
    } finally {
      loading = false;
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      fetchHistory();
    }
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
      fetchHistory();
    }
  }

  async function fetchRemainingBalance() {
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append("Authorization", "Bearer 3d8aaaa1-1ae8-4bc0-94fe-0a952adb3c18");
    const requestOptions = {
      method: "GET",
      headers: myHeaders,
      redirect: "follow"
    };
    try {
      const userId = $page.data.user?.id;
      if (!userId) {
        throw new Error("User ID not found");
      }

      // First, get all subscriptions
      const subscriptionsResponse = await fetch(`https://gpt-portal-lagoapi.sandbox.pressingly.net/api/v1/subscriptions?external_customer_id=${userId}&page=1`, requestOptions);
      const subscriptionsData = await subscriptionsResponse.json();
      
      // Get the first subscription
      const firstSubscription = subscriptionsData.subscriptions[0];
      if (!firstSubscription) {
        throw new Error("No subscription found");
      }
      // Use the subscription ID to get the balance
      const balanceResponse = await fetch(`https://gpt-portal-lagoapi.sandbox.pressingly.net/api/v1/customers/${userId}/current_usage?external_subscription_id=${firstSubscription.external_id}`, requestOptions);
      const balanceData = await balanceResponse.json();
      
      // Calculate remaining balance
      const totalSucceededAmount = balanceData.customer_usage.total_succeeded_amount_cents;
      const usedUnits = parseFloat(balanceData.customer_usage.charges_usage[0].units);
      const remainingBalanceCents = totalSucceededAmount - usedUnits;
      const balanceInDollars = remainingBalanceCents / 100; // Convert cents to dollars
      
      remainingBalance = `Remaining Balance: $${balanceInDollars.toFixed(2)}`;
    } catch (error) {
      console.error(error);
      remainingBalance = "Error fetching balance";
    }
  }

  onMount(() => {
    fetchHistory();
    fetchRemainingBalance();
  });
</script>

<h1 class="text-2xl font-bold mb-4">Query History</h1>
<div class="text-lg font-semibold mb-4">{remainingBalance}</div>

{#if loading}
  <div class="py-8 text-center text-gray-500">Loading...</div>
{:else if error}
  <div class="py-8 text-center text-red-500">{error}</div>
{:else}
  <div class="overflow-x-auto rounded-lg shadow border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
    <table class="min-w-full text-sm text-left">
      <thead class="bg-gray-50 dark:bg-gray-800">
        <tr>
          <th class="px-4 py-2 font-semibold">Query ID</th>
          <th class="px-4 py-2 font-semibold">Timestamp</th>
          <th class="px-4 py-2 font-semibold">LLM</th>
          <th class="px-4 py-2 font-semibold">Input Prompt</th>
          <th class="px-4 py-2 font-semibold">Input Tokens</th>
          <th class="px-4 py-2 font-semibold">Input Cost</th>
          <th class="px-4 py-2 font-semibold">Output Tokens</th>
          <th class="px-4 py-2 font-semibold">Output Cost</th>
          <th class="px-4 py-2 font-semibold">Total Cost</th>
        </tr>
      </thead>
      <tbody>
        {#each history as item}
          <tr class="border-t border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800">
            <td class="px-4 py-2 font-mono text-blue-600 dark:text-blue-400">#{item.query_id}</td>
            <td class="px-4 py-2 font-mono">{formatTimestamp(item.timestamp)}</td>
            <td class="px-4 py-2">{item.llm}</td>
            <td class="px-4 py-2 max-w-xs truncate">
              <span class="text-blue-600 underline" title={item.input_prompt}>{item.input_prompt}</span>
            </td>
            <td class="px-4 py-2">{item.input_tokens}</td>
            <td class="px-4 py-2">{item.input_cost}</td>
            <td class="px-4 py-2">{item.output_tokens}</td>
            <td class="px-4 py-2">{item.output_cost}</td>
            <td class="px-4 py-2">{item.total_cost}</td>
          </tr>
        {/each}
      </tbody>
    </table>
    <div class="flex items-center justify-between p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
      <button class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 disabled:opacity-50" on:click={prevPage} disabled={currentPage === 1}>Previous</button>
      <span>Page {currentPage} of {totalPages}</span>
      <button class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 disabled:opacity-50" on:click={nextPage} disabled={currentPage === totalPages}>Next</button>
    </div>
  </div>
{/if}

<style>
  table {
    border-collapse: separate;
    border-spacing: 0;
  }
  th, td {
    white-space: nowrap;
  }
  td.max-w-xs {
    max-width: 20rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style> 