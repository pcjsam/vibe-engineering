#!/usr/bin/env python
"""
specify_ingest.py - Convert project specifications into atomic memories for MongoDB storage

Usage:
    python specify_ingest.py --project_id photos-app --prompt "Build an application..." [--tags ux,photos]

Environment Variables:
    MONGO_URI: MongoDB connection string
    MONGO_DB: Database name (default: skm)
    MONGO_COLLECTION: Collection name (default: memories)
    VOYAGE_API_KEY: Voyage AI API key for embeddings
    VOYAGE_MODEL: Voyage model to use (default: voyage-2)
    SPEC_PINNED_TITLES: Comma-separated substrings to auto-pin memories

Features:
    - Validates prompts contain no tech stack details (WHAT/WHY only)
    - Segments prompts into atomic, typed memories
    - Generates embeddings via Voyage AI
    - Deduplicates based on content hash
    - Auto-pins important memories
    - Outputs summary and formatted table
"""

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime
from textwrap import dedent
from typing import List, Dict, Any, Optional, Tuple

import certifi
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table

# Load environment variables
load_dotenv()

# Constants
TECH_STACK_PATTERN = r'\b(react|vue|vite|sql|sqlite|docker|redis|s3|kafka|k8s|kubernetes|api endpoint|grpc|protobuf|orm|aws|gcp|azure|cloudflare|tailwind|sass|redux|zustand|next\.js)\b'

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


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert project specifications into atomic memories"
    )
    parser.add_argument(
        "--project_id",
        required=True,
        help="Project identifier (e.g., photos-app)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="WHAT/WHY specification prompt"
    )
    parser.add_argument(
        "--tags",
        help="Comma-separated tags (e.g., ux,photos,albums)",
        default=""
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Skip database insertion, only show what would be inserted"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output inserted documents as JSON (excluding embeddings)"
    )
    return parser.parse_args()


def validate_prompt(prompt: str) -> None:
    """Validate that prompt contains no tech stack terms."""
    if re.search(TECH_STACK_PATTERN, prompt.lower()):
        print("Error: tech stack terms not allowed in /specify", file=sys.stderr)
        sys.exit(2)


def segment_to_jsonl(prompt_text: str, tags: List[str]) -> str:
    """
    Segment prompt into JSONL memories using Fireworks AI LLM or fallback.
    """
    api_key = os.getenv("FIREWORKS_API_KEY")

    if not api_key:
        # Return fallback memories
        return FALLBACK_MEMORIES

    model = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/llama-v3p1-70b-instruct")

    try:
        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Tags to use: {', '.join(tags) if tags else 'derive appropriate tags'}\n\nPrompt:\n{prompt_text}"}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Extract the assistant's response
        content = data["choices"][0]["message"]["content"]
        return content.strip()

    except Exception as e:
        print(f"Warning: LLM segmentation failed: {e}", file=sys.stderr)
        print("Falling back to example memories", file=sys.stderr)
        return FALLBACK_MEMORIES


def normalize_and_validate(items: List[Dict]) -> List[Dict]:
    """Normalize and filter memories, dropping invalid ones."""
    valid_kinds = {"vibe", "spec", "constraint", "non_goal", "metric", "example", "open_question"}
    normalized = []

    for item in items:
        # Check content length (max 8 lines)
        if item.get("content", "").count("\n") > 7:
            continue

        # Validate kind
        if item.get("kind") not in valid_kinds:
            continue

        # Normalize fields
        normalized_item = {
            "kind": item["kind"],
            "title": item.get("title", "").strip(),
            "content": item.get("content", "").strip(),
            "tags": item.get("tags", []),
            "deps": item.get("deps", [])
        }

        # Skip if essential fields are empty
        if not normalized_item["title"] or not normalized_item["content"]:
            continue

        normalized.append(normalized_item)

    return normalized


def score_and_pin(item: Dict, pinned_titles: List[str]) -> Dict:
    """Add scoring and pinning metadata to a memory."""
    # Default priorities by kind
    priority_map = {
        "constraint": 0.9,
        "metric": 0.9,
        "vibe": 0.7,
        "spec": 0.6,
        "non_goal": 0.5,
        "example": 0.5,
        "open_question": 0.5
    }

    item["priority"] = priority_map.get(item["kind"], 0.5)

    # Check if should be pinned
    pinned = False
    if pinned_titles:
        title_lower = item["title"].lower()
        for pin_substr in pinned_titles:
            if pin_substr.lower() in title_lower:
                pinned = True
                break

    item["decay"] = {
        "lambda": 0.0003,
        "pinned": pinned
    }

    return item


def embed(text: str) -> Optional[List[float]]:
    """Generate embedding using Voyage AI."""
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        # Return a dummy embedding for testing
        return [0.0] * 1024  # Voyage-2 default dimension

    model = os.getenv("VOYAGE_MODEL", "voyage-2")

    try:
        response = requests.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "input": text,
                "model": model
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
    except Exception as e:
        print(f"Warning: Embedding failed: {e}", file=sys.stderr)
        # Return dummy embedding on failure
        return [0.0] * 1024


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of normalized content."""
    normalized = content.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def upsert_memories(project_id: str, items: List[Dict], dry_run: bool = False) -> Tuple[int, int]:
    """
    Insert memories into MongoDB, skipping duplicates.
    Returns (inserted_count, skipped_count).
    """
    if dry_run:
        return len(items), 0

    # MongoDB connection
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI environment variable is not set")

    client = MongoClient(mongo_uri, tlsCAFile=certifi.where())

    try:
        db_name = os.getenv("MONGO_DB", "master")
        collection_name = os.getenv("MONGO_COLLECTION", "memories")

        db = client[db_name]
        collection = db[collection_name]

        inserted = 0
        skipped = 0

        for item in items:
            # Check for duplicate
            content_hash = item["metadata"]["content_hash"]
            existing = collection.find_one({
                "project_id": project_id,
                "metadata.content_hash": content_hash
            })

            if existing:
                skipped += 1
                continue

            # Insert the document
            collection.insert_one(item)
            inserted += 1

        return inserted, skipped

    finally:
        client.close()


def format_output_table(items: List[Dict]) -> None:
    """Display formatted table of memories."""
    console = Console()

    table = Table(title="📝 Memories", show_header=True, header_style="bold cyan")
    table.add_column("memory_id", style="dim", width=12)
    table.add_column("kind", style="green")
    table.add_column("title", style="white")
    table.add_column("pinned", style="yellow", justify="center")
    table.add_column("priority", style="blue", justify="right")

    for item in items:
        table.add_row(
            item["memory_id"][:8] + "...",
            item["kind"],
            item["title"][:35] + ("..." if len(item["title"]) > 35 else ""),
            "✓" if item["decay"]["pinned"] else "",
            f"{item['priority']:.1f}"
        )

    console.print(table)


def main():
    """Main entry point."""
    args = parse_arguments()

    # Validate prompt
    validate_prompt(args.prompt)

    # Parse tags
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    # Get pinned titles from environment
    pinned_titles = []
    spec_pinned = os.getenv("SPEC_PINNED_TITLES", "")
    if spec_pinned:
        pinned_titles = [t.strip() for t in spec_pinned.split(",") if t.strip()]

    # Segment prompt into memories
    jsonl_text = segment_to_jsonl(args.prompt, tags)

    # Parse JSONL
    raw_items = []
    for line in jsonl_text.strip().split("\n"):
        if line.strip():
            try:
                raw_items.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSONL line: {e}", file=sys.stderr)

    # Normalize and validate
    normalized = normalize_and_validate(raw_items)

    # Build complete documents
    documents = []
    for item in normalized:
        # Add scoring and pinning
        item = score_and_pin(item, pinned_titles)

        # Generate embedding
        embedding = embed(item["content"])

        # Create full document
        doc = {
            "memory_id": str(uuid.uuid4()),
            "project_id": args.project_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "author": "human",
            "kind": item["kind"],
            "title": item["title"],
            "content": item["content"],
            "tags": tags + item.get("tags", []),  # Merge CLI tags with item tags
            "deps": item["deps"],
            "priority": item["priority"],
            "decay": item["decay"],
            "metadata": {
                "source": "speckit.specify",
                "content_hash": compute_content_hash(item["content"])
            },
            "embedding": embedding
        }
        documents.append(doc)

    # Insert into MongoDB
    inserted, skipped = upsert_memories(args.project_id, documents, args.dry_run)

    # Output summary
    print(f"inserted={inserted} skipped={skipped}  (duplicates/invalid)")

    # Output table
    if documents:
        format_output_table(documents)

    # Output JSON if requested
    if args.json:
        # Remove embeddings for JSON output
        json_docs = []
        for doc in documents:
            json_doc = doc.copy()
            json_doc.pop("embedding", None)
            json_docs.append(json_doc)
        print("\n" + json.dumps(json_docs, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())