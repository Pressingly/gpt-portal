import type { ModelInfoMap, ModelInfo } from '$lib/types/model-info';

// Key for storing custom model info in localStorage
const CUSTOM_MODEL_INFO_KEY = 'gpt_portal_custom_model_info';

/**
 * Load custom model info from localStorage
 */
function loadCustomModelInfo(): ModelInfoMap {
  try {
    const storedInfo = localStorage.getItem(CUSTOM_MODEL_INFO_KEY);
    return storedInfo ? JSON.parse(storedInfo) : {};
  } catch (error) {
    console.error('Error loading custom model info:', error);
    return {};
  }
}

/**
 * Save custom model info to localStorage
 */
function saveCustomModelInfo(customInfo: ModelInfoMap): void {
  try {
    localStorage.setItem(CUSTOM_MODEL_INFO_KEY, JSON.stringify(customInfo));
  } catch (error) {
    console.error('Error saving custom model info:', error);
  }
}

/**
 * Default model information data based on the PRD specifications
 */
const defaultModelInfo: ModelInfoMap = {
  // OpenAI Models
  'gpt-4o': {
    company: 'OpenAI',
    tier: 'Standard',
    modelName: 'GPT-4o',
    pricing: {
      inputTokens: 2.50,
      outputTokens: 10.00
    },
    bestUseCases: 'General-purpose tasks requiring a balance between performance and cost, such as content creation, customer support, and data analysis.'
  },
  'gpt-4o-mini': {
    company: 'OpenAI',
    tier: 'Value',
    modelName: 'GPT-4o-mini',
    pricing: {
      inputTokens: 0.15,
      outputTokens: 0.60
    },
    bestUseCases: 'Suitable for applications requiring faster responses and lower latency, such as real-time chat applications and lightweight content generation.'
  },
  'gpt-4.5': {
    company: 'OpenAI',
    tier: 'Pro',
    modelName: 'GPT-4.5',
    pricing: {
      inputTokens: 75.00,
      outputTokens: 150.00
    },
    bestUseCases: 'High-stakes applications requiring nuanced and emotionally intelligent interactions, such as premium customer support, mental health coaching, and complex content creation.'
  },

  // Google Models
  'gemini-2.0-flash': {
    company: 'Google',
    tier: 'Standard',
    modelName: 'Gemini 2.0 Flash',
    pricing: {
      inputTokens: 0.15,
      outputTokens: 0.60
    },
    bestUseCases: 'Ideal for high-volume tasks requiring processing of extensive content, such as large-scale data analysis and document processing.'
  },
  'gemini-2.0-flash-lite': {
    company: 'Google',
    tier: 'Value',
    modelName: 'Gemini 2.0 Flash Lite',
    pricing: {
      inputTokens: 0.075,
      outputTokens: 0.30
    },
    bestUseCases: 'Suitable for applications requiring efficient processing with lower resource consumption, such as mobile applications and embedded systems.'
  },
  'gemini-2.0-pro': {
    company: 'Google',
    tier: 'Pro',
    modelName: 'Gemini 2.0 Pro',
    pricing: {
      inputTokens: 2.50,
      outputTokens: 10.00
    },
    bestUseCases: 'Advanced AI applications requiring higher performance and capabilities, such as complex data modeling and enterprise-level solutions.'
  },

  // Anthropic Models
  'claude-3.7-sonnet': {
    company: 'Anthropic',
    tier: 'Standard',
    modelName: 'Claude 3.7 Sonnet',
    pricing: {
      inputTokens: 3.00,
      outputTokens: 15.00
    },
    bestUseCases: 'Excels in complex problem-solving, particularly in math and coding tasks, as well as agentic coding and legal tasks.'
  },
  'claude-3.5-haiku': {
    company: 'Anthropic',
    tier: 'Value',
    modelName: 'Claude 3.5 Haiku',
    pricing: {
      inputTokens: 0.80,
      outputTokens: 4.00
    },
    bestUseCases: 'Designed for general-purpose tasks requiring a balance between performance and cost, such as content creation and customer support.'
  },
  'claude-3-opus': {
    company: 'Anthropic',
    tier: 'Pro',
    modelName: 'Claude 3 Opus',
    pricing: {
      inputTokens: 15.00,
      outputTokens: 75.00
    },
    bestUseCases: 'Suitable for advanced AI applications requiring higher performance and capabilities, such as complex data analysis and enterprise solutions.'
  },

  // META Models
  'llama-3.1-70b': {
    company: 'META',
    tier: 'Standard',
    modelName: 'Llama 3.1 70B',
    pricing: {
      inputTokens: 2.68,
      outputTokens: 3.54
    },
    bestUseCases: 'Designed for commercial hardware, suitable for applications requiring substantial processing power, such as research and development in AI.'
  },
  'llama-3.2-11b': {
    company: 'META',
    tier: 'Value',
    modelName: 'Llama 3.2 11B',
    pricing: {
      inputTokens: 0.37,
      outputTokens: 0.37
    },
    bestUseCases: 'Suitable for applications requiring a balance between performance and resource efficiency, such as small to medium-scale AI tasks, educational tools, and prototype development.'
  },
  'llama-3.1-405b': {
    company: 'META',
    tier: 'Pro',
    modelName: 'Llama 3.1 405B',
    pricing: {
      inputTokens: 0.90,
      outputTokens: 0.90
    },
    bestUseCases: 'Best suited for high-level research and applications requiring extensive computational power, such as advanced AI research, large-scale data analysis, and complex simulations.'
  },

  // Perplexity Models
  'sonar-pro': {
    company: 'Perplexity',
    tier: 'Standard',
    modelName: 'Sonar Pro',
    pricing: {
      inputTokens: 3.00,
      outputTokens: 15.00,
      requestPrice: 5.00
    },
    bestUseCases: 'Advanced search applications requiring deep content understanding and handling of complex queries, such as in-depth research tasks and comprehensive information retrieval.'
  },
  'sonar': {
    company: 'Perplexity',
    tier: 'Value',
    modelName: 'Sonar',
    pricing: {
      inputTokens: 1.00,
      outputTokens: 1.00,
      requestPrice: 5.00
    },
    bestUseCases: 'Quick and cost-effective search tasks requiring grounded answers, suitable for applications like basic information retrieval and straightforward question-answering systems.'
  },
  'sonar-reasoning-pro': {
    company: 'Perplexity',
    tier: 'Pro',
    modelName: 'Sonar Reasoning Pro',
    pricing: {
      inputTokens: 2.00,
      outputTokens: 8.00,
      requestPrice: 5.00
    },
    bestUseCases: 'Applications requiring multi-step reasoning and problem-solving capabilities, such as complex analytical tasks and decision support systems.'
  },

  // DeepSeek Models
  'deepseek-v3': {
    company: 'DeepSeek',
    tier: 'Standard',
    modelName: 'DeepSeek-V3',
    pricing: {
      inputTokens: 0.07,
      outputTokens: 1.10
    },
    bestUseCases: 'Conversational AI applications like chatbots and customer support systems, benefiting from cost-effective token processing and dynamic response generation.',
    additionalInfo: 'Cache Hit discounted to $0.014 until February 8, 2025. Cache Miss discounted to $0.14. Output tokens discounted to $0.28.'
  },
  'deepseek-r1': {
    company: 'DeepSeek',
    tier: 'Pro',
    modelName: 'DeepSeek-R1',
    pricing: {
      inputTokens: 0.14,
      outputTokens: 2.19
    },
    bestUseCases: 'Tasks requiring logical reasoning and problem-solving, such as research analysis, legal evaluations, and strategic decision-making processes.',
    additionalInfo: 'Output tokens include Chain of Thought and final answer.'
  },

  // XAI Models
  'grok-2-vision': {
    company: 'XAI',
    tier: 'Pro',
    modelName: 'Grok 2-Vision',
    pricing: {
      inputTokens: 2.00,
      outputTokens: 10.00
    },
    bestUseCases: 'Applications integrating visual data processing with language understanding, such as image captioning, visual question answering, and multimedia content analysis.'
  },
  'grok-vision-beta': {
    company: 'XAI',
    tier: 'Standard',
    modelName: 'Grok Vision Beta',
    pricing: {
      inputTokens: 5.00,
      outputTokens: 15.00
    },
    bestUseCases: 'Grok Vision Beta is best suited for analyzing and understanding images through tasks like captioning, visual question answering, and extracting information from screenshots or charts.'
  }
};

// Combine default and custom model info
let modelInfo: ModelInfoMap = { ...defaultModelInfo };

// Initialize with custom model info from localStorage if available
try {
  if (typeof window !== 'undefined') {
    const customInfo = loadCustomModelInfo();
    modelInfo = { ...defaultModelInfo, ...customInfo };
  }
} catch (error) {
  console.error('Error initializing model info:', error);
}

/**
 * Helper function to get model info by ID
 * @param modelId The model ID to look up
 * @returns The model info or undefined if not found
 */
export function getModelInfo(modelId: string) {
  return modelInfo[modelId];
}

/**
 * Helper function to get all model info
 * @returns All model info as an array
 */
export function getAllModelInfo() {
  return Object.entries(modelInfo).map(([id, info]) => ({
    id,
    ...info
  }));
}

/**
 * Update model information for a specific model
 * @param modelId The model ID to update
 * @param info The new model information
 */
export function updateModelInfo(modelId: string, info: Partial<ModelInfo>): void {
  // Get current model info
  const currentInfo = modelInfo[modelId] || {};

  // Update model info
  modelInfo = {
    ...modelInfo,
    [modelId]: {
      ...currentInfo,
      ...info
    }
  };

  // Get custom model info (models that differ from default)
  const customInfo: ModelInfoMap = {};
  Object.entries(modelInfo).forEach(([id, info]) => {
    const defaultInfo = defaultModelInfo[id];
    if (!defaultInfo || JSON.stringify(info) !== JSON.stringify(defaultInfo)) {
      customInfo[id] = info;
    }
  });

  // Save custom model info to localStorage
  if (typeof window !== 'undefined') {
    saveCustomModelInfo(customInfo);
  }
}

/**
 * Add a new model with information
 * @param modelId The model ID to add
 * @param info The model information
 */
export function addModelInfo(modelId: string, info: ModelInfo): void {
  updateModelInfo(modelId, info);
}

/**
 * Reset model information to defaults
 */
export function resetModelInfo(): void {
  modelInfo = { ...defaultModelInfo };
  if (typeof window !== 'undefined') {
    localStorage.removeItem(CUSTOM_MODEL_INFO_KEY);
  }
}
