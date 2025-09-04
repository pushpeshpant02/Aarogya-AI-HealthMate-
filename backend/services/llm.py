from dotenv import load_dotenv
from pathlib import Path
from typing import List, Optional
import os

# Load env file (fallback if not already loaded by main.py)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)


class LLMClient:
    """LLM facade. Uses OpenAI when configured, falls back to a safe default."""

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # ⚠️ Hardcoded API key (testing only, replace with your own key)
      

    def generate(self, prompt: str, context_blocks: Optional[List[str]] = None) -> str:
        context = "\n\n".join(context_blocks or [])
        if self.api_key:
            try:
                # Lazy import to avoid hard dependency if not configured
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key)
                full_prompt = (
                    "You are a cautious healthcare assistant. Provide general guidance only;"
                    " avoid diagnosis.\n\nContext:\n" + context + "\n\nUser:\n" + prompt
                )
                resp = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You provide general, safe health guidance only."},
                        {"role": "user", "content": full_prompt},
                    ],
                    temperature=0.3,
                )
                return (resp.choices[0].message.content or "").strip() or "Please drink water and rest."
            except Exception as e:
                return f"⚠️ LLM error: {str(e)}"

        # Fallback when no API key or error
        return "Please drink water and rest."
