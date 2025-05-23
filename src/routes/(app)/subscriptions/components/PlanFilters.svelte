<script lang="ts">
  import { priceRange, sortOption } from '../stores';
  import { getContext } from 'svelte';

  // Get i18n context
  const i18n = getContext('i18n');

  // Sort options
  const sortOptions = [
    { value: 'price-asc', label: $i18n.t('Price: Low to High') },
    { value: 'price-desc', label: $i18n.t('Price: High to Low') },
    { value: 'name-asc', label: $i18n.t('Name: A to Z') }
  ];

  // Handle price range change
  function handleMinPriceChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const min = parseInt(target.value);
    priceRange.update(range => [min, range[1]]);
  }

  function handleMaxPriceChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const max = parseInt(target.value);
    priceRange.update(range => [range[0], max]);
  }

  // Handle sort option change
  function handleSortChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    sortOption.set(target.value as 'price-asc' | 'price-desc' | 'name-asc');
  }
</script>

<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Price Range Filter -->
    <div class="filter-group">
      <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {$i18n.t('Price Range')}
      </h3>
      <div class="flex items-center space-x-2">
        <input
          type="number"
          min="0"
          max="1000"
          class="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
          value={$priceRange[0]}
          on:change={handleMinPriceChange}
        />
        <span class="text-gray-500 dark:text-gray-400">-</span>
        <input
          type="number"
          min="0"
          max="1000"
          class="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
          value={$priceRange[1]}
          on:change={handleMaxPriceChange}
        />
      </div>
    </div>

    <!-- Sort Options -->
    <div class="filter-group">
      <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {$i18n.t('Sort By')}
      </h3>
      <select
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-800 dark:text-white"
        value={$sortOption}
        on:change={handleSortChange}
      >
        {#each sortOptions as option}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    </div>
  </div>
</div>
