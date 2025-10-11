import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models import Project, Note, Edge, Fact
from mongodb_client import MongoDBClient
from voyageai_client import VoyageAIClient
from config import config


class MemoryService:
    def __init__(self):
        mongodb_config = config.get_mongodb_config()
        voyageai_config = config.get_voyageai_config()
        
        self.mongodb = MongoDBClient(
            uri=mongodb_config.get("uri"),
            database=mongodb_config.get("database", "speckit"),
            collection="notes",  # We'll use different collections
            vector_index=mongodb_config.get("vector_index", "notes_vector_index")
        )
        
        self.voyageai = VoyageAIClient(
            api_key=voyageai_config.get("api_key"),
            model=voyageai_config.get("model", "voyage-code-2")
        )
        
        # Get database handle for different collections
        self.db = self.mongodb._get_database()
        self.projects_collection = self.db.projects
        self.notes_collection = self.db.notes
        self.edges_collection = self.db.edges
        self.facts_collection = self.db.facts
    
    async def create_project(self, slug: str, repo_url: str, owners: List[str] = None) -> Project:
        """Create a new project."""
        project = Project(
            slug=slug,
            repo_url=repo_url,
            owners=owners or []
        )
        
        # Insert into MongoDB
        result = self.projects_collection.insert_one(project.model_dump())
        project.id = str(result.inserted_id)
        
        return project
    
    def get_project_by_slug(self, slug: str) -> Optional[Project]:
        """Get project by slug."""
        doc = self.projects_collection.find_one({"slug": slug})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return Project(**doc)
        return None
    
    async def create_note(self, note: Note) -> Note:
        """Create a new note with embedding."""
        # Generate embedding for the note
        if note.text and not note.embedding:
            embedding_result = self.voyageai.embed([note.text], input_type="document")
            note.embedding = embedding_result.embeddings[0]
        
        # Insert into MongoDB
        note_dict = note.model_dump()
        result = self.notes_collection.insert_one(note_dict)
        note.id = str(result.inserted_id)
        
        return note
    
    def get_notes_by_project(self, project_id: str, note_type: str = None) -> List[Note]:
        """Get notes for a project, optionally filtered by type."""
        query = {"project_id": project_id}
        if note_type:
            query["type"] = note_type
        
        notes = []
        for doc in self.notes_collection.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            notes.append(Note(**doc))
        
        return notes
    
    async def create_edge(self, edge: Edge) -> Edge:
        """Create a relationship edge between notes."""
        edge_dict = edge.model_dump()
        result = self.edges_collection.insert_one(edge_dict)
        edge.id = str(result.inserted_id)
        return edge
    
    async def vector_search_notes(self, query_text: str, project_id: str, 
                                 note_types: List[str] = None, limit: int = 10) -> List[Note]:
        """Search notes using vector similarity."""
        # Generate embedding for query
        embedding_result = self.voyageai.embed([query_text], input_type="query")
        query_embedding = embedding_result.embeddings[0]
        
        # Build aggregation pipeline
        must_filters = [
            {"knnBeta": {"vector": query_embedding, "path": "embedding", "k": limit * 2}},
            {"equals": {"path": "project_id", "value": project_id}}
        ]
        
        should_filters = []
        if note_types:
            for note_type in note_types:
                should_filters.append({"equals": {"path": "type", "value": note_type}})
        
        compound_query = {"must": must_filters}
        if should_filters:
            compound_query["should"] = should_filters
        
        pipeline = [
            {
                "$search": {
                    "index": self.mongodb.vector_index_name,
                    "compound": compound_query
                }
            },
            {"$limit": limit},
            {
                "$addFields": {
                    "score": {"$meta": "searchScore"}
                }
            }
        ]
        
        notes = []
        try:
            for doc in self.notes_collection.aggregate(pipeline):
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                # Remove score field for Note model
                if "score" in doc:
                    del doc["score"]
                notes.append(Note(**doc))
        except Exception as e:
            # Fallback to text search if vector search fails
            print(f"Vector search failed, falling back to text search: {e}")
            query = {"project_id": project_id, "$text": {"$search": query_text}}
            if note_types:
                query["type"] = {"$in": note_types}
            
            for doc in self.notes_collection.find(query).limit(limit):
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                notes.append(Note(**doc))
        
        return notes
    
    async def seed_principles_and_guidelines(self, project_id: str, 
                                           principles: List[Dict[str, Any]], 
                                           guidelines: List[Dict[str, Any]]) -> List[Note]:
        """Seed a project with default principles and guidelines."""
        notes = []
        
        # Create principle notes
        for principle_data in principles:
            note = Note(
                project_id=project_id,
                type="principle",
                title=principle_data["title"],
                text=principle_data["text"],
                tags=principle_data.get("tags", []),
                created_by="system"
            )
            created_note = await self.create_note(note)
            notes.append(created_note)
        
        # Create guideline notes
        for guideline_data in guidelines:
            note = Note(
                project_id=project_id,
                type="guideline",
                title=guideline_data["title"],
                text=guideline_data["text"],
                tags=guideline_data.get("tags", []),
                created_by="system"
            )
            created_note = await self.create_note(note)
            notes.append(created_note)
        
        return notes
    
    def close(self):
        """Close database connections."""
        self.mongodb.close()