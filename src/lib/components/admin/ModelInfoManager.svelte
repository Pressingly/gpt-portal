<script lang="ts">
  import { getContext, onMount } from 'svelte';
  import type { ModelInfo } from '$lib/types/model-info';
  import {
    getModels,
    getModelById,
    updateModelMetadata,
    refreshModelMetadata,
    refreshAllMetadata
  } from '$lib/apis/models';
  import { toast } from 'svelte-sonner';

  const i18n = getContext('i18n');

  let allModels: any[] = [];
  let availableModels: any[] = [];
  let selectedModelId: string = '';
  let loading = true;
  let saving = false;
  let refreshing = false;
  let bulkRefreshing = false;
  let forceUpdate = false;

  // Form fields
  let company = '';
  let tier = 'Standard';
  let modelName = '';
  let inputTokenPrice = 0;
  let outputTokenPrice = 0;
  let requestPrice: number | null = null;
  let bestUseCases = '';
  let additionalInfo = '';

  // Fetch models and populate the form
  async function fetchModels() {
    try {
      loading = true;
      const token = localStorage.token;
      const models = await getModels(token);

      allModels = models;

      // Filter for base models only
      availableModels = models.filter((model: any) => model.base_model_id === null);

      loading = false;
    } catch (err) {
      console.error('Error fetching models:', err);
      toast.error($i18n.t('Failed to load models'));
      loading = false;
    }
  }

  // Load model info when a model is selected
  async function loadModelInfo(id: string) {
    if (!id) return;

    try {
      loading = true;
      const token = localStorage.token;
      const model = await getModelById(token, id);

      if (model && model.meta) {
        const meta = model.meta;
        company = meta.company || '';
        tier = meta.tier || 'Standard';
        modelName = meta.name || model.name;
        inputTokenPrice = meta.pricing?.inputTokens || 0;
        outputTokenPrice = meta.pricing?.outputTokens || 0;
        requestPrice = meta.pricing?.requestPrice || null;
        bestUseCases = meta.best_use_cases || '';
        additionalInfo = meta.additionalInfo || '';
      } else {
        // Reset form if no metadata
        resetForm();
        modelName = model.name || id;
      }

      loading = false;
    } catch (err) {
      console.error('Error loading model info:', err);
      toast.error($i18n.t('Failed to load model information'));
      loading = false;
    }
  }

  // Save model info
  async function saveModelInfo() {
    if (!selectedModelId) {
      toast.error($i18n.t('Please select a model'));
      return;
    }

    saving = true;

    try {
      const token = localStorage.token;

      // Create metadata object
      const metadata = {
        company,
        tier,
        name: modelName,
        pricing: {
          inputTokens: inputTokenPrice,
          outputTokens: outputTokenPrice,
          ...(requestPrice !== null ? { requestPrice } : {})
        },
        best_use_cases: bestUseCases,
        ...(additionalInfo ? { additionalInfo } : {})
      };

      // Update model metadata
      await updateModelMetadata(token, selectedModelId, metadata);

      toast.success($i18n.t('Model information saved'));
    } catch (err) {
      console.error('Error saving model info:', err);
      toast.error($i18n.t('Failed to save model information'));
    } finally {
      saving = false;
    }
  }

  // Refresh model metadata from master data
  async function refreshMetadata() {
    if (!selectedModelId) {
      toast.error($i18n.t('Please select a model'));
      return;
    }

    refreshing = true;

    try {
      const token = localStorage.token;

      // Refresh model metadata
      await refreshModelMetadata(token, selectedModelId, forceUpdate);

      // Reload model info
      await loadModelInfo(selectedModelId);

      toast.success($i18n.t('Model information refreshed'));
    } catch (err) {
      console.error('Error refreshing model info:', err);
      toast.error($i18n.t('Failed to refresh model information'));
    } finally {
      refreshing = false;
    }
  }

  // Refresh all model metadata
  async function refreshAllModels() {
    bulkRefreshing = true;

    try {
      const token = localStorage.token;

      // Refresh all model metadata
      const result = await refreshAllMetadata(token, forceUpdate);

      // Reload current model if selected
      if (selectedModelId) {
        await loadModelInfo(selectedModelId);
      }

      // Reload models list
      await fetchModels();

      toast.success(
        $i18n.t('All models refreshed: {updated} updated, {skipped} unchanged', {
          updated: result.updated,
          skipped: result.skipped
        })
      );
    } catch (err) {
      console.error('Error refreshing all models:', err);
      toast.error($i18n.t('Failed to refresh all models'));
    } finally {
      bulkRefreshing = false;
    }
  }

  // Reset form fields
  function resetForm() {
    company = '';
    tier = 'Standard';
    modelName = '';
    inputTokenPrice = 0;
    outputTokenPrice = 0;
    requestPrice = null;
    bestUseCases = '';
    additionalInfo = '';
  }

  onMount(() => {
    fetchModels();
  });

  $: if (selectedModelId) {
    loadModelInfo(selectedModelId);
  }
</script>

<div class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
  <h2 class="text-xl font-bold mb-4 text-gray-800 dark:text-gray-200">{$i18n.t('Model Information Manager')}</h2>

  {#if loading}
    <div class="flex justify-center items-center h-40">
      <p class="text-gray-500 dark:text-gray-400">{$i18n.t('Loading models...')}</p>
    </div>
  {:else}
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="model-select">
        {$i18n.t('Select Model')}
      </label>
      <div class="flex gap-2">
        <select
          id="model-select"
          class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
          bind:value={selectedModelId}
        >
          <option value="">{$i18n.t('-- Select a model --')}</option>
          <optgroup label={$i18n.t('Base Models')}>
            {#each availableModels as model}
              <option value={model.id}>{model.name || model.id}</option>
            {/each}
          </optgroup>
        </select>
      </div>
    </div>

    <!-- Force update checkbox and refresh buttons -->
    <div class="mb-6 flex flex-col gap-4">
      <div class="flex items-center">
        <input
          type="checkbox"
          id="force-update"
          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          bind:checked={forceUpdate}
        />
        <label for="force-update" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
          {$i18n.t('Force update (overwrite existing values)')}
        </label>
      </div>

      <div class="flex gap-2">
        {#if selectedModelId}
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            on:click={refreshMetadata}
            disabled={refreshing}
          >
            {refreshing ? $i18n.t('Refreshing...') : $i18n.t('Refresh Selected Model')}
          </button>
        {/if}

        <button
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          on:click={refreshAllModels}
          disabled={bulkRefreshing}
        >
          {bulkRefreshing ? $i18n.t('Refreshing All...') : $i18n.t('Refresh All Models')}
        </button>
      </div>
    </div>

    {#if selectedModelId}
      <form on:submit|preventDefault={saveModelInfo} class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Company -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="company">
              {$i18n.t('Company')}
            </label>
            <input
              id="company"
              type="text"
              class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
              bind:value={company}
              placeholder="OpenAI, Google, Anthropic, etc."
            />
          </div>

          <!-- Tier -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="tier">
              {$i18n.t('Tier')}
            </label>
            <select
              id="tier"
              class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
              bind:value={tier}
            >
              <option value="Value">{$i18n.t('Value')}</option>
              <option value="Standard">{$i18n.t('Standard')}</option>
              <option value="Pro">{$i18n.t('Pro')}</option>
            </select>
          </div>

          <!-- Model Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="model-name">
              {$i18n.t('Model Name')}
            </label>
            <input
              id="model-name"
              type="text"
              class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
              bind:value={modelName}
              placeholder="GPT-4o, Claude 3.5 Haiku, etc."
            />
          </div>

          <!-- Input Token Price -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="input-token-price">
              {$i18n.t('Input Token Price (per 1M tokens)')}
            </label>
            <input
              id="input-token-price"
              type="number"
              step="0.001"
              min="0"
              class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
              bind:value={inputTokenPrice}
            />
          </div>

          <!-- Output Token Price -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="output-token-price">
              {$i18n.t('Output Token Price (per 1M tokens)')}
            </label>
            <input
              id="output-token-price"
              type="number"
              step="0.001"
              min="0"
              class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
              bind:value={outputTokenPrice}
            />
          </div>

          <!-- Request Price -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="request-price">
              {$i18n.t('Request Price (per 1K requests, optional)')}
            </label>
            <input
              id="request-price"
              type="number"
              step="0.01"
              min="0"
              class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
              bind:value={requestPrice}
              placeholder="Optional"
            />
          </div>
        </div>

        <!-- Best Use Cases -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="best-use-cases">
            {$i18n.t('Best Use Cases')}
          </label>
          <textarea
            id="best-use-cases"
            rows="3"
            class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
            bind:value={bestUseCases}
            placeholder="Describe the best use cases for this model..."
          ></textarea>
        </div>

        <!-- Additional Info -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" for="additional-info">
            {$i18n.t('Additional Information (optional)')}
          </label>
          <textarea
            id="additional-info"
            rows="2"
            class="block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-gray-100"
            bind:value={additionalInfo}
            placeholder="Any additional information about the model..."
          ></textarea>
        </div>

        <div class="flex justify-end">
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={saving}
          >
            {saving ? $i18n.t('Saving...') : $i18n.t('Save Model Information')}
          </button>
        </div>
      </form>
    {/if}
  {/if}
</div>
