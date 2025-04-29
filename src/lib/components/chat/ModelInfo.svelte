<script lang="ts">
  import { getContext, onMount } from 'svelte';
  import type { ModelInfo as ModelInfoType } from '$lib/types/model-info';
  import Modal from '$lib/components/common/Modal.svelte';
  import Tooltip from '$lib/components/common/Tooltip.svelte';
  import { getModelById, getModels } from '$lib/apis/models';
  import { toast } from 'svelte-sonner';

  const i18n = getContext('i18n');

  export let show = false;
  export let modelId: string = '';

  let modelInfo: ModelInfoType | undefined;
  let showAllModels = false;
  let allModels: any[] = [];
  let loading = true;
  let error = false;

  // Fetch all models from the API
  async function fetchModels() {
    try {
      loading = true;
      error = false;

      // Get models from the API
      const token = localStorage.token;
      const models = await getModels(token);

      // Process models to extract metadata
      allModels = models.map((model: any) => {
        const meta = model.meta || {};
        return {
          id: model.id,
          modelName: meta.name || model.name,
          company: meta.company || 'Unknown',
          tier: meta.tier || 'Standard',
          pricing: meta.pricing || { inputTokens: 0, outputTokens: 0 },
          bestUseCases: meta.best_use_cases || '',
          additionalInfo: meta.additionalInfo || ''
        };
      });

      loading = false;
    } catch (err) {
      console.error('Error fetching models:', err);
      error = true;
      loading = false;
      toast.error($i18n.t('Failed to load model information'));
    }
  }

  // Fetch a specific model by ID
  async function fetchModelById(id: string) {
    try {
      loading = true;
      error = false;

      // Get model from the API
      const token = localStorage.token;
      const model = await getModelById(token, id);

      if (model && model.meta) {
        const meta = model.meta;
        modelInfo = {
          modelName: meta.name || model.name,
          company: meta.company || 'Unknown',
          tier: meta.tier || 'Standard',
          pricing: meta.pricing || { inputTokens: 0, outputTokens: 0 },
          bestUseCases: meta.best_use_cases || '',
          additionalInfo: meta.additionalInfo || ''
        };
      } else {
        // If API doesn't have the info, show error state
        error = true;
        toast.error($i18n.t('Model information not available'));
      }

      loading = false;
    } catch (err) {
      console.error('Error fetching model:', err);
      error = true;
      loading = false;
      toast.error($i18n.t('Failed to load model information'));
    }
  }

  onMount(() => {
    if (!modelId) {
      fetchModels();
    }
  });

  $: {
    if (modelId) {
      fetchModelById(modelId);
      showAllModels = false;
    } else {
      showAllModels = true;
      if (show && allModels.length === 0) {
        fetchModels();
      }
    }
  }

  function formatPrice(price: number): string {
    if (price >= 1) {
      return `$${price.toFixed(2)}`;
    } else {
      return `$${price.toFixed(3)}`;
    }
  }

  function getTierClass(tier: string): string {
    switch (tier) {
      case 'Value':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-800/30 dark:text-blue-300';
      case 'Standard':
        return 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300';
      case 'Pro':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-800/30 dark:text-purple-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700/50 dark:text-gray-300';
    }
  }
</script>

<Modal bind:show>
  <div class="p-4 text-gray-800 dark:text-gray-200">
    {#if showAllModels}
      <div class="flex flex-col space-y-6">
        <h2 class="text-xl font-bold">{$i18n.t('Available Models')}</h2>
        <p class="text-gray-600 dark:text-gray-400">{$i18n.t('Compare costs and capabilities of available models')}</p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {#each allModels as model}
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <div>
                  <h3 class="text-lg font-bold">{model.modelName}</h3>
                  <p class="text-gray-600 dark:text-gray-400">{model.company}</p>
                </div>
                <div>
                  <span class="px-2.5 py-0.5 rounded-full text-sm font-medium {getTierClass(model.tier)}">
                    {model.tier}
                  </span>
                </div>
              </div>

              <div class="mt-2 border-t border-gray-100 dark:border-gray-700/50 pt-2">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-600 dark:text-gray-400">{$i18n.t('Input')}</span>
                  <span class="font-medium text-gray-800 dark:text-gray-200">{formatPrice(model.pricing.inputTokens)} / 1M</span>
                </div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-600 dark:text-gray-400">{$i18n.t('Output')}</span>
                  <span class="font-medium text-gray-800 dark:text-gray-200">{formatPrice(model.pricing.outputTokens)} / 1M</span>
                </div>
                {#if model.pricing.requestPrice}
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-600 dark:text-gray-400">{$i18n.t('Per 1K Requests')}</span>
                    <span class="font-medium text-gray-800 dark:text-gray-200">${model.pricing.requestPrice.toFixed(2)}</span>
                  </div>
                {/if}
              </div>

              <div class="mt-3 text-sm text-gray-700 dark:text-gray-300 line-clamp-3 border-t border-gray-100 dark:border-gray-700/50 pt-2">
                {model.bestUseCases}
              </div>

              <button
                class="mt-4 text-sm text-blue-600 dark:text-blue-400 hover:underline font-medium"
                on:click={() => {
                  modelId = model.id;
                  showAllModels = false;
                  modelInfo = model;
                }}
              >
                {$i18n.t('View details')}
              </button>
            </div>
          {/each}
        </div>
      </div>
    {:else if modelInfo}
      <div class="flex flex-col space-y-6">
        <!-- Header with model name and company -->
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">{modelInfo.modelName}</h2>
            <p class="text-gray-600 dark:text-gray-400">{modelInfo.company}</p>
          </div>
          <div>
            <span class="px-2.5 py-0.5 rounded-full text-sm font-medium {getTierClass(modelInfo.tier)}">
              {modelInfo.tier}
            </span>
          </div>
        </div>

        <!-- Pricing information -->
        <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-100 dark:border-gray-700/50 shadow-sm">
          <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">{$i18n.t('Pricing')}</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span class="text-gray-600 dark:text-gray-400 text-sm">{$i18n.t('Input Tokens')}</span>
              <span class="text-lg font-medium text-gray-800 dark:text-gray-200">
                {formatPrice(modelInfo.pricing.inputTokens)} / 1M tokens
              </span>
            </div>
            <div class="flex flex-col">
              <span class="text-gray-600 dark:text-gray-400 text-sm">{$i18n.t('Output Tokens')}</span>
              <span class="text-lg font-medium text-gray-800 dark:text-gray-200">
                {formatPrice(modelInfo.pricing.outputTokens)} / 1M tokens
              </span>
            </div>
            {#if modelInfo.pricing.requestPrice}
              <div class="flex flex-col md:col-span-2">
                <span class="text-gray-600 dark:text-gray-400 text-sm">{$i18n.t('Price per 1,000 Requests')}</span>
                <span class="text-lg font-medium text-gray-800 dark:text-gray-200">
                  ${modelInfo.pricing.requestPrice.toFixed(2)}
                </span>
              </div>
            {/if}
          </div>

          {#if modelInfo.additionalInfo}
            <div class="mt-3 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700/50 pt-2">
              <Tooltip content={$i18n.t('Additional pricing information')}>
                <div class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                  </svg>
                  <span>{modelInfo.additionalInfo}</span>
                </div>
              </Tooltip>
            </div>
          {/if}
        </div>

        <!-- Best use cases -->
        <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-100 dark:border-gray-700/50 shadow-sm">
          <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">{$i18n.t('Best Use Cases')}</h3>
          <p class="text-gray-700 dark:text-gray-300">{modelInfo.bestUseCases}</p>
        </div>

        <!-- Cost comparison example -->
        <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-100 dark:border-gray-700/50 shadow-sm">
          <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">{$i18n.t('Cost Example')}</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {$i18n.t('Estimated cost for a typical conversation (1,000 input tokens, 2,000 output tokens):')}
          </p>
          <div class="font-medium text-gray-800 dark:text-gray-200 text-lg">
            ${((modelInfo.pricing.inputTokens * 1000 / 1000000) + (modelInfo.pricing.outputTokens * 2000 / 1000000)).toFixed(4)}
          </div>
        </div>

        <div class="flex justify-center mt-2">
          <button
            class="px-4 py-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-md transition-colors font-medium"
            on:click={() => {
              modelId = '';
              showAllModels = true;
            }}
          >
            {$i18n.t('View all models')}
          </button>
        </div>
      </div>
    {:else}
      <div class="flex justify-center items-center h-40">
        <p class="text-gray-500 dark:text-gray-400">{$i18n.t('Model information not available')}</p>
      </div>
    {/if}
  </div>
</Modal>
