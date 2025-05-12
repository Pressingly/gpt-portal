<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';
  import posthog from '$lib/posthog';
  import '$lib/styles/survey.css';

  export let surveyId: string;
  export let visible = false;

  let surveyContainer: HTMLDivElement;
  let surveyRendered = false;
  const dispatch = createEventDispatcher();

  onMount(() => {
    if (visible && surveyId && !surveyRendered) {
      renderSurvey();
    }
  });

  $: if (visible && surveyId && !surveyRendered) {
    renderSurvey();
  }

  function renderSurvey() {
    if (!surveyContainer) return;

    try {
      // Render the survey in the container
      posthog.renderSurvey(surveyId, '#survey-container');
      surveyRendered = true;

      // Track that the survey was shown
      posthog.capture('survey shown', {
        $survey_id: surveyId
      });
    } catch (error) {
      console.error('Error rendering survey:', error);
      close();
    }
  }

  function close() {
    // Track that the survey was dismissed if it was rendered
    if (surveyRendered) {
      posthog.capture('survey dismissed', {
        $survey_id: surveyId
      });
    }

    surveyRendered = false;
    dispatch('close');
  }
</script>

{#if visible}
  <div
    class="survey-overlay"
    transition:fade={{ duration: 200 }}
    role="dialog"
    aria-modal="true"
    aria-labelledby="survey-title"
  >
    <div
      class="survey-modal"
      role="document"
      tabindex="-1"
    >
      <button class="close-button" on:click={close} aria-label="Close survey">×</button>
      <div bind:this={surveyContainer} id="survey-container">
        <p id="survey-title">Loading survey...</p>
      </div>
    </div>
    <!-- Invisible overlay for clicking outside to close -->
    <button
      class="overlay-button"
      on:click={close}
      aria-label="Close survey"
    ></button>
  </div>
{/if}

<style>
  .survey-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .survey-modal {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    position: relative;
  }

  .close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
  }

  #survey-container {
    min-height: 100px;
  }

  .overlay-button {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
    background: transparent;
    border: none;
    z-index: -1;
    cursor: pointer;
  }

  /* Additional styling for PostHog survey elements */
  :global(.survey-box) {
    font-family: inherit;
    color: inherit;
  }

  :global(.survey-question) {
    font-size: 1.2rem;
    margin-bottom: 1rem;
  }

  :global(.survey-textarea) {
    width: 100%;
    min-height: 100px;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  :global(.survey-button) {
    background-color: var(--primary-color, #000);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  :global(.survey-button:hover) {
    opacity: 0.9;
  }

  :global(.survey-footer-branding) {
    font-size: 0.8rem;
    color: #666;
    margin-top: 1rem;
  }

  :global(.survey-thank-you-message) {
    text-align: center;
    padding: 2rem 0;
  }
</style>
