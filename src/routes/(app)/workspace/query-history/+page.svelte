<script lang="ts">
  import { onMount } from 'svelte';

  type QueryHistoryItem = {
    query_id: string;
    timestamp: string;
    llm: string;
    input_prompt: string;
    input_tokens: number;
    input_cost: string;
    output_tokens: number;
    output_cost: string;
    total_cost: string;
  };

  // Mock data matching the screenshot (rem_balance removed)
  const mockHistory: QueryHistoryItem[] = [
    {
      query_id: '1042',
      timestamp: '04/07/25 10:45 AM',
      llm: 'GPT-4o',
      input_prompt: 'Explain the difference...',
      input_tokens: 42,
      input_cost: '$0.05',
      output_tokens: 1235,
      output_cost: '$0.20',
      total_cost: '$0.25',
    },
    {
      query_id: '1041',
      timestamp: '04/07/25 10:42 AM',
      llm: 'Claude 3.7',
      input_prompt: 'Explain the difference...',
      input_tokens: 25,
      input_cost: '$0.10',
      output_tokens: 2450,
      output_cost: '$0.40',
      total_cost: '$0.50',
    },
    {
      query_id: '1040',
      timestamp: '04/07/25 10:36 AM',
      llm: 'Claude 3.7',
      input_prompt: 'Explain quantum computing...',
      input_tokens: 38,
      input_cost: '$0.05',
      output_tokens: 1850,
      output_cost: '$0.20',
      total_cost: '$0.25',
    },
    {
      query_id: '1039',
      timestamp: '04/07/25 10:30 AM',
      llm: 'Llama 3.1',
      input_prompt: 'Write code for sorting algorithm...',
      input_tokens: 52,
      input_cost: '$0.03',
      output_tokens: 3280,
      output_cost: '$0.17',
      total_cost: '$0.20',
    },
    {
      query_id: '1038',
      timestamp: '04/07/25 10:22 AM',
      llm: 'GPT-4o',
      input_prompt: 'How can I optimize database...',
      input_tokens: 35,
      input_cost: '$0.04',
      output_tokens: 1872,
      output_cost: '$0.21',
      total_cost: '$0.25',
    },
    {
      query_id: '1037',
      timestamp: '04/07/25 10:15 AM',
      llm: 'Llama 3.1',
      input_prompt: 'How can I optimize database...',
      input_tokens: 40,
      input_cost: '$0.15',
      output_tokens: 4120,
      output_cost: '$0.60',
      total_cost: '$0.75',
    },
    {
      query_id: '1036',
      timestamp: '04/07/25 10:08 AM',
      llm: 'Claude 3.7',
      input_prompt: 'Write a product description for...',
      input_tokens: 45,
      input_cost: '$0.05',
      output_tokens: 1540,
      output_cost: '$0.20',
      total_cost: '$0.25',
    },
    {
      query_id: '1035',
      timestamp: '04/07/25 10:00 AM',
      llm: 'GPT-4o',
      input_prompt: 'Summarize the key points from...',
      input_tokens: 120,
      input_cost: '$0.15',
      output_tokens: 850,
      output_cost: '$0.10',
      total_cost: '$0.25',
    },
  ];

  let history: QueryHistoryItem[] = [];
  let loading = true;
  let error = '';
  let page = 1;
  let pageSize = 8;
  let totalPages = Math.ceil(mockHistory.length / pageSize);

  // TODO: Replace this with fetch from FASTAPI backend
  // async function fetchHistory() {
  //   loading = true;
  //   error = '';
  //   try {
  //     const res = await fetch(`/api/ledger?page=${page}&page_size=${pageSize}`);
  //     if (!res.ok) throw new Error('Failed to fetch query history');
  //     const data = await res.json();
  //     history = data.items;
  //     totalPages = data.total_pages || 1;
  //   } catch (e) {
  //     error = e.message || 'Unknown error';
  //   } finally {
  //     loading = false;
  //   }
  // }

  function updateHistoryPage() {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    history = mockHistory.slice(start, end);
    loading = false;
  }

  function prevPage() {
    if (page > 1) {
      page--;
      updateHistoryPage();
    }
  }
  function nextPage() {
    if (page < totalPages) {
      page++;
      updateHistoryPage();
    }
  }

  onMount(() => {
    updateHistoryPage();
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
            <td class="px-4 py-2">{item.timestamp}</td>
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