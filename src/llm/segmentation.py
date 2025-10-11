"""LLM-based prompt segmentation for specification ingestion."""
import os
import json
from typing import List, Dict

import requests
from dotenv import load_dotenv


# Constants for specification segmentation
LLM_SYSTEM_PROMPT = """You convert WHAT/WHY product prompts into JSONL "memories".
Fields: kind ∈ {vibe,spec,constraint,non_goal,metric,example,open_question}, title, content (≤ 8 lines), tags[], deps[].
Rules: no implementation/tech details; one idea per memory; create open_question if info is missing; concise & reusable; tags from a small set like ["ux","photos","albums","a11y","perf"].
Output JSONL only."""

FALLBACK_MEMORIES = """
{"kind": "spec", "title": "Photo album organization", "content": "Application organizes photos into separate albums", "tags": ["photos", "albums"], "deps": []}
{"kind": "spec", "title": "Album date grouping", "content": "Albums are grouped by date", "tags": ["albums", "organization"], "deps": []}
{"kind": "spec", "title": "Drag and drop reordering", "content": "Albums can be re-organized by dragging and dropping on the main page", "tags": ["ux", "albums"], "deps": []}
{"kind": "constraint", "title": "Albums cannot be nested", "content": "Albums are never contained within other albums", "tags": ["albums", "constraint"], "deps": []}
{"kind": "spec", "title": "Tiled photo previews", "content": "Within each album, photos are previewed in a tile-like interface", "tags": ["photos", "ux"], "deps": []}
{"kind": "open_question", "title": "Tile size configuration", "content": "What should be the default tile size and can users customize it?", "tags": ["ux", "photos"], "deps": []}
""".strip()


class SpecificationSegmenter:
    """Segments prompts into atomic memory specifications using LLM."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize specification segmenter.

        Args:
            api_key: Fireworks API key. If not provided, reads from FIREWORKS_API_KEY env var.
            model: Model to use. If not provided, reads from FIREWORKS_MODEL env var or uses default.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("FIREWORKS_API_KEY")
        self.model = model or os.getenv(
            "FIREWORKS_MODEL", "accounts/fireworks/models/llama-v3p1-70b-instruct"
        )

    def segment_to_jsonl(self, prompt_text: str, tags: List[str]) -> str:
        """
        Segment prompt into JSONL memories using Fireworks AI LLM or fallback.

        Args:
            prompt_text: The specification prompt to segment.
            tags: List of tags to suggest to the LLM.

        Returns:
            JSONL string containing segmented memories.
        """
        if not self.api_key:
            # Return fallback memories
            return FALLBACK_MEMORIES

        try:
            response = requests.post(
                "https://api.fireworks.ai/inference/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": LLM_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Tags to use: {', '.join(tags) if tags else 'derive appropriate tags'}\n\nPrompt:\n{prompt_text}",
                        },
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Extract the assistant's response
            content = data["choices"][0]["message"]["content"]
            return content.strip()

        except Exception as e:
            print(f"Warning: LLM segmentation failed: {e}")
            print("Falling back to example memories")
            return FALLBACK_MEMORIES

    def parse_jsonl(self, jsonl_text: str) -> List[Dict]:
        """
        Parse JSONL text into list of dictionaries.

        Args:
            jsonl_text: JSONL formatted string.

        Returns:
            List of parsed JSON objects.
        """
        items = []
        for line in jsonl_text.strip().split("\n"):
            if line.strip():
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse JSONL line: {e}")
        return items
