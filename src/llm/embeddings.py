"""Embedding generation using Voyage AI."""
import os
from typing import Optional, List

import requests
from dotenv import load_dotenv


class VoyageEmbeddings:
    """Client for generating embeddings using Voyage AI."""

    def __init__(self, api_key: Optional[str] = None, model: str = "voyage-2"):
        """
        Initialize Voyage AI embeddings client.

        Args:
            api_key: Voyage API key. If not provided, reads from VOYAGE_API_KEY env var.
            model: Model name to use. Defaults to "voyage-2".
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        self.model = model
        self.default_dimension = 1024  # Default for voyage-2

    def embed(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for given text.

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding, or None if API key not set.
        """
        if not self.api_key:
            # Return a dummy embedding for testing
            return [0.0] * self.default_dimension

        try:
            response = requests.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"input": text, "model": self.model},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"Warning: Embedding failed: {e}")
            # Return dummy embedding on failure
            return [0.0] * self.default_dimension

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embeddings corresponding to input texts.
        """
        if not self.api_key:
            return [[0.0] * self.default_dimension for _ in texts]

        try:
            response = requests.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"input": texts, "model": self.model},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            print(f"Warning: Batch embedding failed: {e}")
            # Return dummy embeddings on failure
            return [[0.0] * self.default_dimension for _ in texts]
