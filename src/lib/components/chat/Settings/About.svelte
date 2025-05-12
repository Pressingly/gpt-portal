<script lang="ts">
	import { WEBUI_VERSION } from '$lib/constants';
</script>

<div class="flex flex-col h-full justify-between space-y-3 text-sm mb-6">
	<div class="space-y-3">
		<div class="mb-2.5 text-sm font-medium flex space-x-2 items-center">
			<div>Askii Version: v{WEBUI_VERSION}</div>
		</div>
		<div class="flex flex-col gap-2 mt-4">
			<a href="https://askii.ai" target="_blank" class="underline text-blue-600">Link to the platform: Askii.ai</a>
			<a href="https://askiimall.ai" target="_blank" class="underline text-blue-600">Link to the marketplace: AskiiMall.ai</a>
		</div>
	</div>
</div>
