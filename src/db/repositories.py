"""Repository classes for database operations."""
from typing import List, Optional, Dict, Any, Tuple

from .client import MongoDBClient


class TeamRepository:
    """Repository for team member operations."""

    def __init__(self, db_client: MongoDBClient):
        """
        Initialize team repository.

        Args:
            db_client: MongoDB client instance.
        """
        self.db_client = db_client

    def fetch_all_members(self) -> List[str]:
        """
        Fetch all team member names.

        Returns:
            List of team member names.

        Raises:
            Exception: If there's an error fetching team members.
        """
        try:
            database = self.db_client.get_database("master")
            collection = database.get_collection("team")

            query = {}
            documents = collection.find(query)

            team_members = []
            for document in documents:
                team_members.append(document["name"])

            return team_members
        except Exception as e:
            raise Exception(f"Error fetching team members: {e}")


class MemoryRepository:
    """Repository for memory/specification operations."""

    def __init__(self, db_client: MongoDBClient):
        """
        Initialize memory repository.

        Args:
            db_client: MongoDB client instance.
        """
        self.db_client = db_client

    def upsert_memories(
        self, project_id: str, items: List[Dict[str, Any]], db_name: str = "master", collection_name: str = "memories"
    ) -> Tuple[int, int]:
        """
        Insert memories into MongoDB, skipping duplicates.

        Args:
            project_id: Project identifier.
            items: List of memory documents to insert.
            db_name: Database name. Defaults to "master".
            collection_name: Collection name. Defaults to "memories".

        Returns:
            Tuple of (inserted_count, skipped_count).
        """
        db = self.db_client.get_database(db_name)
        collection = db[collection_name]

        inserted = 0
        skipped = 0

        for item in items:
            # Check for duplicate
            content_hash = item["metadata"]["content_hash"]
            existing = collection.find_one(
                {"project_id": project_id, "metadata.content_hash": content_hash}
            )

            if existing:
                skipped += 1
                continue

            # Insert the document
            collection.insert_one(item)
            inserted += 1

        return inserted, skipped

    def find_by_project(
        self, project_id: str, db_name: str = "master", collection_name: str = "memories"
    ) -> List[Dict[str, Any]]:
        """
        Find all memories for a given project.

        Args:
            project_id: Project identifier.
            db_name: Database name. Defaults to "master".
            collection_name: Collection name. Defaults to "memories".

        Returns:
            List of memory documents.
        """
        db = self.db_client.get_database(db_name)
        collection = db[collection_name]

        return list(collection.find({"project_id": project_id}))
