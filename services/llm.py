from typing import Optional


class LLMClient:
    """Interface for Large Language Model interactions.

    Replace method bodies with real calls (e.g., OpenAI) later.
    """

    def __init__(self, model_name: str | None = None, api_key: Optional[str] = None):
        self.model_name = model_name or "gpt-4o-mini"
        self.api_key = api_key

    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Return generated text given a prompt and optional retrieved context."""
        _ = (prompt, context)
        # Placeholder behavior; implement real provider call here
        return (
            "This is general advice, not a medical diagnosis. Please drink water and rest."
        )


