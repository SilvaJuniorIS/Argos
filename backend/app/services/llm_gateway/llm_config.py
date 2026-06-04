LLM_TASK_MODELS = {
    "chat": "openrouter/auto",
    "summary": "google/gemini-2.5-flash",
    "document_analysis": "google/gemini-2.5-pro",
    "legal_draft": "anthropic/claude-sonnet-4",
    "fallback": "openai/gpt-4o-mini",
}

DEFAULT_TEMPERATURES = {
    "chat": 0.4,
    "summary": 0.2,
    "document_analysis": 0.2,
    "legal_draft": 0.25,
    "fallback": 0.2,
}
