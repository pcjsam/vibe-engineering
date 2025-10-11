"""Database module for MongoDB interactions."""
from .client import MongoDBClient
from .operations import (
    upsert_document,
    get_document,
    get_documents,
    delete_document,
    delete_documents,
    insert_document,
    insert_documents,
)

__all__ = [
    "MongoDBClient",
    "upsert_document",
    "get_document",
    "get_documents",
    "delete_document",
    "delete_documents",
    "insert_document",
    "insert_documents",
]
