"""LLM client for Fireworks AI integration."""
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from fireworks import LLM


class FireworksClient:
    """Client for interacting with Fireworks AI LLM services."""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-v3p1-terminus"):
        """
        Initialize Fireworks AI client.

        Args:
            api_key: Fireworks API key. If not provided, reads from FIREWORKS_API_KEY env var.
            model: Model name to use. Defaults to "deepseek-v3p1-terminus".
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("FIREWORKS_API_KEY")

        if not self.api_key:
            raise ValueError("FIREWORKS_API_KEY environment variable is not set")

        self.model = model
        self._client = LLM(model=self.model, deployment_type="auto", api_key=self.api_key)

    def generate_with_schema(self, prompt: str, schema: Dict[str, Any], schema_name: str = "ResponseSchema") -> str:
        """
        Generate a response following a specific JSON schema.

        Args:
            prompt: User prompt to send to the LLM.
            schema: Pydantic model JSON schema to enforce.
            schema_name: Name of the schema. Defaults to "ResponseSchema".

        Returns:
            Generated response content as a string.
        """
        response = self._client.chat.completions.create(
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": schema,
                },
            },
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Simple chat completion without schema enforcement.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Sampling temperature. Defaults to 0.7.
            max_tokens: Maximum tokens to generate. Defaults to 2000.

        Returns:
            Generated response content as a string.
        """
        response = self._client.chat.completions.create(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content
