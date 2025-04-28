<script lang="ts">
  import { getContext, onMount } from 'svelte';
  import { getModelInfo, getAllModelInfo, updateModelInfo, resetModelInfo } from '$lib/config/model-info';
  import type { ModelInfo } from '$lib/types/model-info';
  import { getModels } from '$lib/apis/models';
  import { toast } from 'svelte-sonner';

  const i18n = getContext('i18n');

  let allModels: any[] = [];
  let availableModels: any[] = [];
  let selectedModelId: string = '';
  let loading = true;
  let saving = false;

  // Form fields
  let company = '';
  let tier = 'Standard';
  let modelName = '';
  let inputTokenPrice = 0;
  let outputTokenPrice = 0;
  let requestPrice: number | null = null;
  let bestUseCases = '';
  let additionalInfo = '';

  // Fetch all models from the API
  async function fetchModels() {
    try {
      loading = true;

      // Get models from the API
      const token = localStorage.token;
      const models = await getModels(token);

      // Store all models
      allModels = models;

      // Get models that don't have info yet
      updateAvailableModels();

      loading = false;
    } catch (err) {
      console.error('Error fetching models:', err);
      loading = false;
      toast.error($i18n.t('Failed to load models'));
    }
  }

  // Update the list of available models
  function updateAvailableModels() {
    // Get all model info
    const modelInfoList = getAllModelInfo();
    const modelInfoIds = modelInfoList.map(info => info.id);

    // Filter models that don't have info yet
    availableModels = allModels.filter(model => !modelInfoIds.includes(model.id));
  }

  // Load model info when a model is selected
  function loadModelInfo() {
    if (!selectedModelId) {
      resetForm();
      return;
    }

    const info = getModelInfo(selectedModelId);

    if (info) {
      company = info.company || '';
      tier = info.tier || 'Standard';
      modelName = info.modelName || '';
      inputTokenPrice = info.pricing?.inputTokens || 0;
      outputTokenPrice = info.pricing?.outputTokens || 0;
      requestPrice = info.pricing?.requestPrice || null;
      bestUseCases = info.bestUseCases || '';
      additionalInfo = info.additionalInfo || '';
    } else {
      // If no info exists, try to get the name from the model list
      const model = allModels.find(m => m.id === selectedModelId);
      if (model) {
        modelName = model.name || selectedModelId;
      } else {
        modelName = selectedModelId;
      }

      // Reset other fields
      company = '';
      tier = 'Standard';
      inputTokenPrice = 0;
      outputTokenPrice = 0;
      requestPrice = null;
      bestUseCases = '';
      additionalInfo = '';
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

  // Save model info
  function saveModelInfo() {
    if (!selectedModelId) {
      toast.error($i18n.t('Please select a model'));
      return;
    }

    saving = true;

    try {
      // Create model info object
      const info: ModelInfo = {
        company,
        tier: tier as any,
        modelName,
        pricing: {
          inputTokens: inputTokenPrice,
          outputTokens: outputTokenPrice,
          ...(requestPrice !== null ? { requestPrice } : {})
        },
        bestUseCases,
        ...(additionalInfo ? { additionalInfo } : {})
      };

      // Update model info
      updateModelInfo(selectedModelId, info);

      // Update available models
      updateAvailableModels();

      toast.success($i18n.t('Model information saved'));
    } catch (err) {
      console.error('Error saving model info:', err);
      toast.error($i18n.t('Failed to save model information'));
    } finally {
      saving = false;
    }
  }

  // Reset all model info to defaults
  function handleResetAll() {
    if (confirm($i18n.t('Are you sure you want to reset all model information to defaults?'))) {
      resetModelInfo();
      updateAvailableModels();
      resetForm();
      selectedModelId = '';
      toast.success($i18n.t('All model information reset to defaults'));
    }
  }

  // Watch for changes to selectedModelId
  $: if (selectedModelId) {
    loadModelInfo();
  }

  onMount(() => {
    fetchModels();
  });
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
          <optgroup label={$i18n.t('Models with Information')}>
            {#each getAllModelInfo() as model}
              <option value={model.id}>{model.modelName} ({model.id})</option>
            {/each}
          </optgroup>
          {#if availableModels.length > 0}
            <optgroup label={$i18n.t('Models without Information')}>
              {#each availableModels as model}
                <option value={model.id}>{model.name || model.id}</option>
              {/each}
            </optgroup>
          {/if}
        </select>
        <button
          class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          on:click={handleResetAll}
        >
          {$i18n.t('Reset All')}
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
