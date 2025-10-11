"""Generic CRUD operations for MongoDB."""
from typing import Dict, Any, List, Optional

from .client import MongoDBClient


def upsert_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any],
    document: Dict[str, Any],
    upsert: bool = True
) -> Any:
    """
    Upsert a single document in MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        query: Query to find existing document.
        document: Document data to insert/update.
        upsert: If True, insert if document doesn't exist. Defaults to True.

    Returns:
        Result of the update operation.
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    result = collection.update_one(query, {"$set": document}, upsert=upsert)
    return result


def get_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Get a single document from MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        query: Query criteria to find the document.

    Returns:
        Document if found, None otherwise.
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    return collection.find_one(query)


def get_documents(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any],
    limit: Optional[int] = None,
    sort: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]:
    """
    Get multiple documents from MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        query: Query criteria to find documents.
        limit: Maximum number of documents to return. None for all.
        sort: List of (field, direction) tuples for sorting.

    Returns:
        List of documents matching the query.
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    cursor = collection.find(query)

    if sort:
        cursor = cursor.sort(sort)

    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)


def delete_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> int:
    """
    Delete a single document from MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        query: Query criteria to find the document to delete.

    Returns:
        Number of documents deleted (0 or 1).
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    result = collection.delete_one(query)
    return result.deleted_count


def delete_documents(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> int:
    """
    Delete multiple documents from MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        query: Query criteria to find documents to delete.

    Returns:
        Number of documents deleted.
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    result = collection.delete_many(query)
    return result.deleted_count


def insert_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    document: Dict[str, Any]
) -> Any:
    """
    Insert a single document into MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        document: Document to insert.

    Returns:
        Inserted document ID.
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    result = collection.insert_one(document)
    return result.inserted_id


def insert_documents(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    documents: List[Dict[str, Any]]
) -> List[Any]:
    """
    Insert multiple documents into MongoDB.

    Args:
        db_client: MongoDB client instance.
        db_name: Database name.
        collection_name: Collection name.
        documents: List of documents to insert.

    Returns:
        List of inserted document IDs.
    """
    db = db_client.get_database(db_name)
    collection = db[collection_name]

    result = collection.insert_many(documents)
    return result.inserted_ids
