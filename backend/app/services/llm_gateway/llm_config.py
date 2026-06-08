LLM_TASK_MODELS = {
    "chat": "openrouter/free",
    "summary": "openrouter/free",
    "document_analysis": "openrouter/free",
    "legal_draft": "openrouter/free",
    "fallback": "openai/gpt-4o-mini",
}

DEFAULT_TEMPERATURES = {
    "chat": 0.4,
    "summary": 0.2,
    "document_analysis": 0.2,
    "legal_draft": 0.25,
    "fallback": 0.2,
}
