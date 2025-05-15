<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import { config, user } from '$lib/stores';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import { toast } from 'svelte-sonner';

	// Define a type for the i18n context
	interface I18n {
		t: (key: string, params?: Record<string, any>) => string;
	}

	const i18n = getContext('i18n');

	// State variables
	let iframeHeight = 600; // Default height
	let loading = true;
	let error = false;
	let errorMessage = '';
	let iframeElement: HTMLIFrameElement;
	let storefrontUrl = '';
	let loadTimeout: ReturnType<typeof setTimeout>;

	// Function to handle messages from the iframe
	const handleMessage = (event: MessageEvent) => {
		// Validate the origin of the message
		if (!storefrontUrl || !event.origin.includes(new URL(storefrontUrl).hostname)) {
			console.warn('Received message from untrusted origin:', event.origin);
			return;
		}

		try {
			// Check if the message is about height adjustment
			if (event.data && typeof event.data === 'object') {
				// Handle STOREFRONT_EMBED_HEIGHT message type
				if (event.data.type === 'STOREFRONT_EMBED_HEIGHT' && typeof event.data.height === 'number') {
					// Update the iframe height
					iframeHeight = event.data.height;
					console.log('Updated iframe height to:', iframeHeight);
				}
			}
		} catch (err) {
			console.error('Error processing message from iframe:', err);
		}
	};

	// Function to handle iframe load event
	const handleIframeLoad = () => {
		loading = false;
		clearTimeout(loadTimeout);
	};

	// Function to handle iframe error event
	const handleIframeError = () => {
		loading = false;
		error = true;
		errorMessage = $i18n.t('Failed to load subscription plans. Please try again later.');
		clearTimeout(loadTimeout);
		toast.error(errorMessage);
	};

	onMount(() => {
		// Get the storefront URL from the config
		// We need to use a type assertion to access potential properties
		const configObj = $config as any;

		// Access the storefront URL from the moneta.storefront section of the config
		if (configObj?.moneta?.storefront?.enabled && configObj?.moneta?.storefront?.url) {
			// Use the redirect_url if available, otherwise use the base URL
			if (configObj.moneta.storefront.redirect_url) {
				storefrontUrl = configObj.moneta.storefront.redirect_url;
			} else {
				storefrontUrl = configObj.moneta.storefront.url;
				// Append /plan if it's not already included
				if (!storefrontUrl.endsWith('/plan')) {
					storefrontUrl = `${storefrontUrl}/plan`;
				}
			}
			console.log('Storefront config:', storefrontUrl);

		} else {
			// If the storefront is not enabled or URL is not found
			console.error('Storefront is not enabled or URL not found in config:', configObj);
			error = true;
			errorMessage = $i18n.t('Storefront is not configured. Please contact your administrator.');
			loading = false;
			toast.error(errorMessage);
			return;
		}

		// Add event listener for messages from the iframe
		window.addEventListener('message', handleMessage);

		// Set a timeout for loading the iframe
		loadTimeout = setTimeout(() => {
			if (loading) {
				loading = false;
				error = true;
				errorMessage = $i18n.t('Subscription plans are taking too long to load. Please try again later.');
				toast.error(errorMessage);
			}
		}, 30000); // 30 seconds timeout
	});

	onDestroy(() => {
		// Clean up event listeners and timeouts
		window.removeEventListener('message', handleMessage);
		clearTimeout(loadTimeout);
	});
</script>

<svelte:head>
	<title>{$i18n.t('Subscription Plans')}</title>
</svelte:head>

<div class="flex flex-col w-full h-full overflow-hidden bg-white dark:bg-gray-900">
	<!-- Header -->
	<div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
		<h1 class="text-xl font-semibold text-gray-800 dark:text-white">
			{$i18n.t('Subscription Plans')}
		</h1>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		{#if error}
			<div class="flex flex-col items-center justify-center h-64 text-center">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-16 w-16 text-gray-400 dark:text-gray-500 mb-4"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
					/>
				</svg>
				<p class="text-lg font-medium text-gray-800 dark:text-white mb-2">
					{$i18n.t('Unable to load subscription plans')}
				</p>
				<p class="text-gray-600 dark:text-gray-300 max-w-md">
					{errorMessage || $i18n.t('Please try again later or contact your administrator.')}
				</p>
				<button
					class="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
					on:click={() => window.location.reload()}
				>
					{$i18n.t('Try Again')}
				</button>
			</div>
		{:else if storefrontUrl}
			<div class="w-full h-full relative">
				<!-- {#if loading}
					<div class="absolute inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-gray-900/80 z-10">
						<Spinner className="h-8 w-8" />
						<p class="mt-4 text-gray-600 dark:text-gray-300">
							{$i18n.t('Loading subscription plans...')}
						</p>
					</div>
				{/if} -->
				<iframe
					bind:this={iframeElement}
					src={storefrontUrl}
					title={$i18n.t('Subscription Plans')}
					style="width: 100%; height: {iframeHeight}px; border: none; transition: height 0.3s ease;"
					sandbox="allow-scripts allow-forms allow-same-origin allow-popups"
					allow="payment"
					on:load={handleIframeLoad}
					on:error={handleIframeError}
				></iframe>
			</div>
		{:else}
			<div class="flex flex-col items-center justify-center h-64 text-center">
				<p class="text-lg font-medium text-gray-800 dark:text-white mb-2">
					{$i18n.t('No subscription plans available')}
				</p>
				<p class="text-gray-600 dark:text-gray-300 max-w-md">
					{$i18n.t('Please contact your administrator for more information.')}
				</p>
			</div>
		{/if}
	</div>
</div>
