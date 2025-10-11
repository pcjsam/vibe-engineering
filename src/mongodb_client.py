import os
import time
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()


class MongoDBClient:
    def __init__(self, uri: Optional[str] = None, database: str = "speckit", 
                 collection: str = "specifications", vector_index: str = "spec_vector_index"):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = database
        self.collection_name = collection
        self.vector_index_name = vector_index
        self.client = None
        self.database = None
        self.collection = None
    
    def _get_client(self) -> MongoClient:
        if self.client is None:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        return self.client
    
    def _get_database(self):
        if self.database is None:
            client = self._get_client()
            self.database = client[self.database_name]
        return self.database
    
    def _get_collection(self):
        if self.collection is None:
            database = self._get_database()
            self.collection = database[self.collection_name]
        return self.collection
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            client = self._get_client()
            # Test basic connection
            client.admin.command('ping')
            
            # Test database and collection access
            database = self._get_database()
            collection = self._get_collection()
            
            # Check if vector index exists
            indexes = list(collection.list_indexes())
            vector_index_exists = any(
                idx.get("name") == self.vector_index_name for idx in indexes
            )
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Get MongoDB version
            server_info = client.server_info()
            version = server_info.get("version", "unknown")
            
            return {
                "success": True,
                "latency_ms": round(latency, 2),
                "database": self.database_name,
                "collection": self.collection_name,
                "vector_index_exists": vector_index_exists,
                "vector_index_name": self.vector_index_name,
                "mongodb_version": version,
                "document_count": collection.count_documents({}),
                "message": "MongoDB connection successful"
            }
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "message": f"MongoDB connection failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"MongoDB connection failed: {str(e)}"
            }
    
    def create_vector_index(self, vector_field: str = "embedding", 
                          dimensions: int = 1024, similarity: str = "cosine") -> Dict[str, Any]:
        try:
            collection = self._get_collection()
            
            # Create vector search index
            index_definition = {
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        vector_field: {
                            "dimensions": dimensions,
                            "similarity": similarity,
                            "type": "knnVector"
                        }
                    }
                }
            }
            
            # Note: This requires MongoDB Atlas with vector search enabled
            # For local MongoDB, you would need to use a different approach
            collection.create_search_index(
                definition=index_definition,
                name=self.vector_index_name
            )
            
            return {
                "success": True,
                "message": f"Vector index '{self.vector_index_name}' created successfully",
                "index_name": self.vector_index_name,
                "vector_field": vector_field,
                "dimensions": dimensions,
                "similarity": similarity
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create vector index: {str(e)}"
            }
    
    def insert_document(self, content: str, embedding: List[float], 
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            collection = self._get_collection()
            
            document = {
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": time.time()
            }
            
            result = collection.insert_one(document)
            
            return {
                "success": True,
                "document_id": str(result.inserted_id),
                "message": "Document inserted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to insert document: {str(e)}"
            }
    
    def vector_search(self, query_embedding: List[float], limit: int = 10, 
                     score_threshold: float = 0.7) -> Dict[str, Any]:
        try:
            collection = self._get_collection()
            
            # MongoDB Atlas vector search aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": self.vector_index_name,
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 10,
                        "limit": limit
                    }
                },
                {
                    "$addFields": {
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$match": {
                        "score": {"$gte": score_threshold}
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "message": f"Found {len(results)} similar documents"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Vector search failed: {str(e)}"
            }
    
    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.collection = None
    
    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "uri": self.uri.replace(self.uri.split('@')[-1].split('/')[0], '***') if '@' in self.uri else self.uri,
            "database": self.database_name,
            "collection": self.collection_name,
            "vector_index": self.vector_index_name
        }