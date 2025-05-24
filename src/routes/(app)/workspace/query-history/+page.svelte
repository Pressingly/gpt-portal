<script lang="ts">
  import { onMount } from 'svelte';
  import { getQueryHistory, type QueryHistoryItem } from '$lib/apis/query_history';
  import { getToken } from '$lib/utils/auth';
  import { page } from '$app/stores';
  import { user } from '$lib/stores';

  let history: QueryHistoryItem[] = [];
  let loading = true;
  let error = '';
  let currentPage = 1;
  let pageSize = 20;
  let totalPages = 1;
  let remainingBalance = 'Loading...';
  let selectedPrompt = null; // For modal display
  let showPromptModal = false; // Controls visibility of the prompt modal

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
      // Get user ID from auth session
      const userId = $user?.id;
      
      if (!userId) {
        throw new Error("User ID not found in auth session");
      }
      
      console.log('User ID from auth:', userId);

      // First, get all subscriptions
      const subscriptionsUrl = `https://gpt-portal-lagoapi.sandbox.pressingly.net/api/v1/subscriptions?external_customer_id=${userId}&page=1`;
      console.log('Fetching subscriptions from:', subscriptionsUrl);
      
      const subscriptionsResponse = await fetch(subscriptionsUrl, requestOptions);
      const subscriptionsData = await subscriptionsResponse.json();
      console.log('Subscriptions response:', subscriptionsData);
      
      // Get the first subscription
      const firstSubscription = subscriptionsData.subscriptions[0];
      if (!firstSubscription) {
        throw new Error("No subscription found");
      }

      // Use the subscription ID to get the balance
      const balanceUrl = `https://gpt-portal-lagoapi.sandbox.pressingly.net/api/v1/customers/${userId}/current_usage?external_subscription_id=${firstSubscription.external_id}`;
      console.log('Fetching balance from:', balanceUrl);
      
      const balanceResponse = await fetch(balanceUrl, requestOptions);
      const balanceData = await balanceResponse.json();
      console.log('Balance response:', balanceData);
      
      // Calculate remaining balance
      const totalSucceededAmount = balanceData.customer_usage.total_succeeded_amount_cents;
      const usedUnits = parseFloat(balanceData.customer_usage.charges_usage[0].units);
      const remainingBalanceCents = totalSucceededAmount - usedUnits;
      const balanceInDollars = remainingBalanceCents / 100; // Convert cents to dollars
      
      remainingBalance = `Remaining Balance: $${balanceInDollars.toFixed(2)}`;
    } catch (error) {
      console.error('Error in fetchRemainingBalance:', error);
      if (error instanceof Error && error.message === "No subscription found") {
        remainingBalance = "No subscription found";
      } else {
        remainingBalance = "Error fetching balance";
      }
    }
  }

  function openPromptModal(prompt) {
    selectedPrompt = prompt;
    showPromptModal = true;
  }

  function closePromptModal() {
    showPromptModal = false;
  }

  onMount(() => {
    fetchHistory();
    fetchRemainingBalance();
  });
</script>

<!-- Modal for displaying full prompt -->
{#if showPromptModal && selectedPrompt}
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" on:click={closePromptModal}>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-3xl w-full max-h-[80vh] overflow-hidden" on:click|stopPropagation>
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 class="text-lg font-medium">Input Prompt</h3>
        <button class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300" on:click={closePromptModal}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="p-4 overflow-y-auto max-h-[calc(80vh-8rem)]">
        <p class="whitespace-pre-wrap">{selectedPrompt}</p>
      </div>
    </div>
  </div>
{/if}

<div class="flex justify-between items-center mb-4">
  <div>
    <h1 class="text-2xl font-bold">Query History</h1>
    <div class="text-lg font-semibold mt-1">{remainingBalance}</div>
  </div>
</div>

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
            <td class="px-4 py-2">{formatTimestamp(item.timestamp)}</td>
            <td class="px-4 py-2">{item.llm}</td>
            <td class="px-4 py-2 max-w-xs">
              <div 
                class="text-blue-600 hover:text-blue-800 cursor-pointer truncate hover:underline" 
                on:click={() => openPromptModal(item.input_prompt)}
              >
                {#if item.input_prompt && item.input_prompt.length > 50}
                  {item.input_prompt.substring(0, 50)}...
                {:else}
                  {item.input_prompt || 'No prompt available'}
                {/if}
              </div>
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