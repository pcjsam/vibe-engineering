"""MongoDB client connection management."""
import os
from typing import Optional

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database


class MongoDBClient:
    """Manages MongoDB connections and provides access to database resources."""

    def __init__(self, uri: Optional[str] = None):
        """
        Initialize MongoDB client.

        Args:
            uri: MongoDB connection URI. If not provided, reads from MONGODB_URI env var.
        """
        load_dotenv()
        self.uri = uri or os.getenv("MONGODB_URI")

        if not self.uri:
            raise ValueError("MONGODB_URI environment variable is not set")

        self._client: Optional[MongoClient] = None

    def connect(self) -> MongoClient:
        """Establish connection to MongoDB."""
        if self._client is None:
            self._client = MongoClient(self.uri, tlsCAFile=certifi.where())
        return self._client

    def get_database(self, db_name: str = "master") -> Database:
        """
        Get a database instance.

        Args:
            db_name: Name of the database. Defaults to "master".

        Returns:
            Database instance.
        """
        client = self.connect()
        return client.get_database(db_name)

    def close(self):
        """Close the MongoDB connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
