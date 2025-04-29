"""
Master data for model information.

This file contains standardized information about LLM models, including:
- Company that created the model
- Tier classification (Value, Standard, Pro)
- Pricing information (input tokens, output tokens, request-based pricing)
- Best use cases
- Additional information

This data is used to populate model metadata for base models.
"""

import re
from typing import Dict, Any, Optional


# Master data for model information
MODEL_INFO_MASTER = {
    # OpenAI Models
    "gpt-4o": {
        "company": "OpenAI",
        "tier": "Pro",
        "name": "GPT-4o",
        "pricing": {
            "inputTokens": 5.00,
            "outputTokens": 15.00
        },
        "best_use_cases": "Advanced reasoning, complex instructions, code generation, creative content creation, and detailed analysis. Suitable for professional applications requiring high accuracy and nuanced understanding."
    },
    "gpt-4-turbo": {
        "company": "OpenAI",
        "tier": "Pro",
        "name": "GPT-4 Turbo",
        "pricing": {
            "inputTokens": 10.00,
            "outputTokens": 30.00
        },
        "best_use_cases": "Advanced reasoning, complex instructions, code generation, creative content creation, and detailed analysis. Suitable for professional applications requiring high accuracy and nuanced understanding."
    },
    "gpt-4": {
        "company": "OpenAI",
        "tier": "Pro",
        "name": "GPT-4",
        "pricing": {
            "inputTokens": 30.00,
            "outputTokens": 60.00
        },
        "best_use_cases": "Advanced reasoning, complex instructions, code generation, creative content creation, and detailed analysis. Suitable for professional applications requiring high accuracy and nuanced understanding."
    },
    "gpt-3.5-turbo": {
        "company": "OpenAI",
        "tier": "Standard",
        "name": "GPT-3.5 Turbo",
        "pricing": {
            "inputTokens": 0.50,
            "outputTokens": 1.50
        },
        "best_use_cases": "General-purpose tasks, content generation, summarization, and conversational AI. Good balance between performance and cost."
    },
    
    # Anthropic Models
    "claude-3-opus": {
        "company": "Anthropic",
        "tier": "Pro",
        "name": "Claude 3 Opus",
        "pricing": {
            "inputTokens": 15.00,
            "outputTokens": 75.00
        },
        "best_use_cases": "Complex reasoning, nuanced understanding, and detailed analysis. Excellent for professional applications requiring high accuracy and sophisticated responses."
    },
    "claude-3-sonnet": {
        "company": "Anthropic",
        "tier": "Standard",
        "name": "Claude 3 Sonnet",
        "pricing": {
            "inputTokens": 3.00,
            "outputTokens": 15.00
        },
        "best_use_cases": "Balanced performance for a wide range of tasks including content creation, summarization, and conversational AI. Good balance between quality and cost."
    },
    "claude-3-haiku": {
        "company": "Anthropic",
        "tier": "Value",
        "name": "Claude 3 Haiku",
        "pricing": {
            "inputTokens": 0.25,
            "outputTokens": 1.25
        },
        "best_use_cases": "Fast responses for simpler tasks, basic content generation, and conversational AI. Cost-effective for applications where speed is more important than depth."
    },
    
    # Google Models
    "gemini-1.5-pro": {
        "company": "Google",
        "tier": "Pro",
        "name": "Gemini 1.5 Pro",
        "pricing": {
            "inputTokens": 7.00,
            "outputTokens": 21.00
        },
        "best_use_cases": "Advanced reasoning, multimodal understanding, and complex problem-solving. Excellent for professional applications requiring high accuracy and sophisticated responses."
    },
    "gemini-1.5-flash": {
        "company": "Google",
        "tier": "Standard",
        "name": "Gemini 1.5 Flash",
        "pricing": {
            "inputTokens": 0.35,
            "outputTokens": 1.05
        },
        "best_use_cases": "Fast responses for general-purpose tasks, content generation, and conversational AI. Good balance between performance and cost."
    },
    
    # Mistral Models
    "mistral-large": {
        "company": "Mistral AI",
        "tier": "Pro",
        "name": "Mistral Large",
        "pricing": {
            "inputTokens": 8.00,
            "outputTokens": 24.00
        },
        "best_use_cases": "Advanced reasoning, complex instructions, and detailed analysis. Suitable for professional applications requiring high accuracy and nuanced understanding."
    },
    "mistral-medium": {
        "company": "Mistral AI",
        "tier": "Standard",
        "name": "Mistral Medium",
        "pricing": {
            "inputTokens": 2.70,
            "outputTokens": 8.10
        },
        "best_use_cases": "General-purpose tasks, content generation, summarization, and conversational AI. Good balance between performance and cost."
    },
    "mistral-small": {
        "company": "Mistral AI",
        "tier": "Value",
        "name": "Mistral Small",
        "pricing": {
            "inputTokens": 0.20,
            "outputTokens": 0.60
        },
        "best_use_cases": "Fast responses for simpler tasks, basic content generation, and conversational AI. Cost-effective for applications where speed is more important than depth."
    },
    
    # Ollama Models
    "llama3": {
        "company": "Meta",
        "tier": "Standard",
        "name": "Llama 3",
        "pricing": {
            "inputTokens": 0.00,
            "outputTokens": 0.00
        },
        "best_use_cases": "General-purpose tasks, content generation, summarization, and conversational AI. Open-source model that can be run locally."
    },
    "llama3:8b": {
        "company": "Meta",
        "tier": "Value",
        "name": "Llama 3 (8B)",
        "pricing": {
            "inputTokens": 0.00,
            "outputTokens": 0.00
        },
        "best_use_cases": "Fast responses for simpler tasks, basic content generation, and conversational AI. Smaller open-source model that can be run on less powerful hardware."
    },
    "llama3:70b": {
        "company": "Meta",
        "tier": "Pro",
        "name": "Llama 3 (70B)",
        "pricing": {
            "inputTokens": 0.00,
            "outputTokens": 0.00
        },
        "best_use_cases": "Advanced reasoning, complex instructions, and detailed analysis. Larger open-source model that requires more powerful hardware."
    },
    "mistral": {
        "company": "Mistral AI",
        "tier": "Standard",
        "name": "Mistral",
        "pricing": {
            "inputTokens": 0.00,
            "outputTokens": 0.00
        },
        "best_use_cases": "General-purpose tasks, content generation, summarization, and conversational AI. Open-source model that can be run locally."
    },
    "mixtral": {
        "company": "Mistral AI",
        "tier": "Standard",
        "name": "Mixtral",
        "pricing": {
            "inputTokens": 0.00,
            "outputTokens": 0.00
        },
        "best_use_cases": "General-purpose tasks, content generation, summarization, and conversational AI. Open-source mixture-of-experts model that can be run locally."
    }
}


def normalize_model_id(model_id: str) -> str:
    """
    Normalize a model ID by removing version suffixes and other variations.
    
    Args:
        model_id: The model ID to normalize
        
    Returns:
        Normalized model ID
    """
    # Remove version suffixes like :latest, -preview, etc.
    model_id = re.sub(r'[:@-](latest|preview|[0-9]+(\.[0-9]+)*)', '', model_id)
    
    # Handle specific model families
    if model_id.startswith('gpt-4-'):
        if 'turbo' in model_id:
            return 'gpt-4-turbo'
        return 'gpt-4'
    
    if model_id.startswith('gpt-3.5-'):
        return 'gpt-3.5-turbo'
    
    if model_id.startswith('claude-3-'):
        if 'opus' in model_id:
            return 'claude-3-opus'
        elif 'sonnet' in model_id:
            return 'claude-3-sonnet'
        elif 'haiku' in model_id:
            return 'claude-3-haiku'
    
    if model_id.startswith('gemini-1.5-'):
        if 'pro' in model_id:
            return 'gemini-1.5-pro'
        elif 'flash' in model_id:
            return 'gemini-1.5-flash'
    
    if model_id.startswith('mistral-'):
        if 'large' in model_id:
            return 'mistral-large'
        elif 'medium' in model_id:
            return 'mistral-medium'
        elif 'small' in model_id:
            return 'mistral-small'
    
    if model_id.startswith('llama3'):
        if '8b' in model_id.lower():
            return 'llama3:8b'
        elif '70b' in model_id.lower():
            return 'llama3:70b'
        return 'llama3'
    
    # Return the original ID if no normalization rules match
    return model_id


def get_model_info(model_id: str) -> Optional[Dict[str, Any]]:
    """
    Get model information from the master data.
    
    Args:
        model_id: The model ID to look up
        
    Returns:
        Model information dictionary or None if not found
    """
    # Try exact match first
    if model_id in MODEL_INFO_MASTER:
        return MODEL_INFO_MASTER[model_id]
    
    # Try normalized ID
    normalized_id = normalize_model_id(model_id)
    if normalized_id in MODEL_INFO_MASTER:
        return MODEL_INFO_MASTER[normalized_id]
    
    # Try fuzzy matching
    for master_id, info in MODEL_INFO_MASTER.items():
        if master_id in model_id or model_id in master_id:
            return info
    
    # No match found
    return None
