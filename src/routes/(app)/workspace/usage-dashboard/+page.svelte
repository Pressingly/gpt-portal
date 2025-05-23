<script lang="ts">
  import { onMount } from 'svelte';
  import { getToken } from '$lib/utils/auth';
  import { user } from '$lib/stores';
  import Chart from 'chart.js/auto';
  import { WEBUI_API_BASE_URL } from '$lib/constants';

  let loading = true;
  let error = '';
  let activeTab = 'usage';
  let dateRange = '';
  let charts: { [key: string]: Chart } = {};

  // Chart data
  let queriesData: any[] = [];
  let distributionData = { multi_llm: 0, single_llm: 0 };
  let breakdownData = { Claude: 0, ChatGPT: 0, Gemini: 0 };
  let combinationsData: { combination: string, count: number }[] = [];
  let avgQueriesData: number[] = [];
  let avgQueriesLabels: string[] = [];

  // Date range calculation
  function getDateRange() {
    const today = new Date();
    const endDate = today.toISOString().slice(0, 10);
    const startDate = new Date(today.getTime() - 6 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    return { label: `${startDate} to ${endDate}`, start: startDate, end: endDate };
  }

  async function fetchUsageData() {
    loading = true;
    error = '';
    try {
      const token = await getToken();
      if (!token) throw new Error('No authentication token found');
      const { start, end } = getDateRange();
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Queries over time
      const queriesRes = await fetch(`${WEBUI_API_BASE_URL}/usage_dashboard/llm-queries-over-time?start=${start}&end=${end}`, { headers });
      if (!queriesRes.ok) throw new Error('Failed to fetch queries');
      queriesData = await queriesRes.json();

      // Distribution
      const distRes = await fetch(`${WEBUI_API_BASE_URL}/usage_dashboard/llm-distribution?start=${start}&end=${end}`, { headers });
      if (!distRes.ok) throw new Error('Failed to fetch distribution');
      distributionData = await distRes.json();

      // Breakdown
      const breakdownRes = await fetch(`${WEBUI_API_BASE_URL}/usage_dashboard/llm-breakdown?start=${start}&end=${end}`, { headers });
      if (!breakdownRes.ok) throw new Error('Failed to fetch breakdown');
      breakdownData = await breakdownRes.json();

      // Combinations (new endpoint)
      const comboRes = await fetch(`${WEBUI_API_BASE_URL}/usage_dashboard/llm-combinations?start=${start}&end=${end}`, { headers });
      if (!comboRes.ok) throw new Error('Failed to fetch combinations');
      combinationsData = await comboRes.json();

      avgQueriesLabels = queriesData.map(d => d.day);
      avgQueriesData = queriesData.map(d => d.Total);

      // Initialize charts
      setTimeout(() => initializeCharts(), 0);
    } catch (e: any) {
      error = e.message || 'Unknown error';
    } finally {
      loading = false;
    }
  }

  function initializeCharts() {
    // Destroy old charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    // Line Chart: Queries per LLM Over Time
    const queriesCtx = document.getElementById('queriesChart') as HTMLCanvasElement;
    if (queriesCtx) {
      charts.queries = new Chart(queriesCtx, {
        type: 'line',
        data: {
          labels: queriesData.map(d => d.day),
          datasets: [
            { label: 'Claude', data: queriesData.map(d => d.Claude), borderColor: '#3b82f6', backgroundColor: '#3b82f6', fill: false },
            { label: 'ChatGPT', data: queriesData.map(d => d.ChatGPT), borderColor: '#22c55e', backgroundColor: '#22c55e', fill: false },
            { label: 'Gemini', data: queriesData.map(d => d.Gemini), borderColor: '#f59e42', backgroundColor: '#f59e42', fill: false },
            { label: 'Total', data: queriesData.map(d => d.Total), borderColor: '#ef4444', backgroundColor: '#ef4444', borderDash: [5,5], fill: false }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          layout: { padding: { left: 0, right: 0 } },
          scales: { x: { beginAtZero: true }, y: { beginAtZero: true } }
        }
      });
    }

    // Doughnut Chart: Multi-LLM Query Distribution
    const distCtx = document.getElementById('distributionChart') as HTMLCanvasElement;
    if (distCtx) {
      charts.distribution = new Chart(distCtx, {
        type: 'doughnut',
        data: {
          labels: ['Multi-LLM', 'Single LLM'],
          datasets: [{ data: [distributionData.multi_llm, distributionData.single_llm], backgroundColor: ['#22c55e', '#e5e7eb'] }]
        },
        options: { plugins: { legend: { position: 'bottom' } }, maintainAspectRatio: false }
      });
    }

    // Doughnut Chart: LLM Usage Breakdown
    const breakdownCtx = document.getElementById('breakdownChart') as HTMLCanvasElement;
    if (breakdownCtx) {
      // Define color mapping for each LLM type
      const colorMap: Record<string, string> = {
        'Claude': '#3b82f6',   // Blue
        'ChatGPT': '#22c55e',  // Green
        'Gemini': '#f59e42',   // Orange
        'Other': '#e5e7eb'     // Gray
      };
      const labels = Object.keys(breakdownData);
      const data = Object.values(breakdownData);
      const backgroundColors = labels.map(label => colorMap[label] || '#e5e7eb');
      charts.breakdown = new Chart(breakdownCtx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{ data, backgroundColor: backgroundColors }]
        },
        options: { plugins: { legend: { position: 'bottom' } }, maintainAspectRatio: false }
      });
    }

    // Bar Chart: Popular LLM Combinations
    const comboBar = document.getElementById('combinationsChart') as HTMLCanvasElement;
    if (comboBar) {
      charts.combinations = new Chart(comboBar, {
        type: 'bar',
        data: {
          labels: combinationsData.map(c => c.combination),
          datasets: [{ label: 'Count', data: combinationsData.map(c => c.count), backgroundColor: '#f59e42' }]
        },
        options: { indexAxis: 'y', plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
      });
    }

    // Bar Chart: Average Queries per Day
    const avgBar = document.getElementById('avgQueriesChart') as HTMLCanvasElement;
    if (avgBar) {
      charts.avg = new Chart(avgBar, {
        type: 'bar',
        data: {
          labels: avgQueriesLabels,
          datasets: [{ label: 'Total Queries', data: avgQueriesData, backgroundColor: '#f59e42' }]
        },
        options: { plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
      });
    }
  }

  onMount(() => {
    const dr = getDateRange();
    dateRange = dr.label;
    fetchUsageData();
    return () => {
      Object.values(charts).forEach(chart => chart.destroy());
    };
  });
</script>

<div class="px-2 md:px-8 py-6">
  <!-- Header -->
  <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
    <div>
      <h1 class="text-2xl font-bold">Usage Analytics</h1>
      <div class="text-gray-500 text-sm mt-1">{dateRange}</div>
    </div>
    <div class="flex items-center gap-2">
      <button class="btn btn-outline border border-gray-300 rounded px-4 py-2 text-sm font-medium hover:bg-gray-100">Export</button>
      <button class="ml-2 p-2 rounded bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1.5M12 19.5V21M4.219 4.219l1.061 1.061M18.72 18.72l1.06 1.06M1.5 12H3m18 0h1.5M4.219 19.781l1.061-1.061M18.72 5.28l1.06-1.06" />
        </svg>
      </button>
    </div>
  </div>

  <!-- Tabs -->
  <div class="flex border-b border-gray-200 mb-6">
    <button class="px-4 py-2 -mb-px border-b-2 font-medium text-sm focus:outline-none transition-all"
      class:selected={activeTab === 'usage'}
      class:border-blue-500={activeTab === 'usage'}
      class:text-blue-600={activeTab === 'usage'}
      on:click={() => activeTab = 'usage'}>
      Usage Metrics
    </button>
    <button class="px-4 py-2 -mb-px border-b-2 font-medium text-sm focus:outline-none transition-all"
      class:selected={activeTab === 'financial'}
      class:border-blue-500={activeTab === 'financial'}
      class:text-blue-600={activeTab === 'financial'}
      on:click={() => activeTab = 'financial'}>
      Financial Metrics
    </button>
  </div>

  {#if loading}
    <div class="py-8 text-center text-gray-500">Loading...</div>
  {:else if error}
    <div class="py-8 text-center text-red-500">{error}</div>
  {:else if activeTab === 'usage'}
    <!-- Main Grid -->
    <div class="grid grid-cols-1 gap-6">
      <!-- Line Chart Card -->
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold mb-4">Queries per LLM Over Time (Day)</h2>
        <div class="h-72">
          <canvas id="queriesChart"></canvas>
        </div>
      </div>

      <!-- 2-Column Grid for Doughnut Charts -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-4">Multi-LLM Query Distribution</h2>
          <div class="h-56 flex items-center justify-center text-gray-400">
            <canvas id="distributionChart"></canvas>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-4">LLM Usage Breakdown</h2>
          <div class="h-56 flex items-center justify-center text-gray-400">
            <canvas id="breakdownChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Popular LLM Combinations Bar Chart -->
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold mb-4">Popular LLM Combinations</h2>
        <div class="h-48 flex items-center justify-center text-gray-400">
          <canvas id="combinationsChart"></canvas>
        </div>
      </div>

      <!-- Average Queries per Day Bar Chart -->
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold mb-4">Average Queries per Day</h2>
        <div class="h-48 flex items-center justify-center text-gray-400">
          <canvas id="avgQueriesChart"></canvas>
        </div>
      </div>
    </div>
  {:else}
    <!-- Financial Metrics Placeholder -->
    <div class="bg-white dark:bg-gray-900 rounded-lg shadow p-6 text-center text-gray-400">
      [Financial Metrics Coming Soon]
    </div>
  {/if}
</div>

<style>
  /* Add any custom styles here */
</style> 