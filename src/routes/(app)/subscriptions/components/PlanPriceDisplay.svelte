<script lang="ts">
  import { calculatePlanDisplayPrice } from '../utils/price-utils';
  import type { Plan } from '../stores/types';
  
  // Props
  export let plan: Plan;
  export let showCurrency: boolean = true;
  export let size: 'small' | 'medium' | 'large' = 'medium';
  export let customCurrency: string | undefined = undefined;
  
  // Determine CSS classes based on size
  $: sizeClass = size === 'small' 
    ? 'text-base' 
    : size === 'large' 
      ? 'text-2xl' 
      : 'text-lg';
</script>

<span class="font-bold {sizeClass} text-gray-900 dark:text-white">
  {calculatePlanDisplayPrice(plan, true, customCurrency)}
</span>
