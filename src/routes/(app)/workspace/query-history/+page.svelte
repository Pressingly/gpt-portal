<script lang="ts">
  import { onMount } from 'svelte';
  import { getQueryHistory, type QueryHistoryItem } from '$lib/apis/query_history';
  import { getToken } from '$lib/utils/auth';

  let history: QueryHistoryItem[] = [];
  let loading = true;
  let error = '';
  let page = 1;
  let pageSize = 8;
  let totalPages = 1;

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
      const data = await getQueryHistory(token, page, pageSize);
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
    if (page > 1) {
      page--;
      fetchHistory();
    }
  }

  function nextPage() {
    if (page < totalPages) {
      page++;
      fetchHistory();
    }
  }

  onMount(() => {
    fetchHistory();
  });
</script>

<h1 class="text-2xl font-bold mb-4">Query History</h1>

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
      <button class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 disabled:opacity-50" on:click={prevPage} disabled={page === 1}>Previous</button>
      <span>Page {page} of {totalPages}</span>
      <button class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 disabled:opacity-50" on:click={nextPage} disabled={page === totalPages}>Next</button>
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