# Classes and Methods

## Overview

This document provides a comprehensive reference for all classes, methods, and functions in the Vibe Engineering codebase, organized by module.

---

## CLI Module (`src/cli/`)

### `commands.py`

Contains all CLI commands implemented using Typer.

#### Global Objects

- **`app`**: `typer.Typer()` - Main Typer application instance

#### Commands

##### `hello(name: str)`

**Description**: Simple greeting command that says hello to the specified person.

**Parameters**:
- `name` (str): Name of the person to greet

**Returns**: None (prints to stdout)

**Example**:
```bash
uv run main.py hello World
# Output: Hello World
```

---

##### `goodbye(name: str)`

**Description**: Simple farewell command that says goodbye to the specified person.

**Parameters**:
- `name` (str): Name of the person to say goodbye to

**Returns**: None (prints to stdout)

**Example**:
```bash
uv run main.py goodbye World
# Output: Goodbye World
```

---

##### `team()`

**Description**: Displays team members from the MongoDB database in a formatted table.

**Parameters**: None

**Returns**: None (prints Rich table to console)

**Behavior**:
- Connects to MongoDB using context manager
- Queries `master.team` collection
- Displays results in a Rich table with columns: #, Name, Status
- Shows total team member count
- Handles errors with user-friendly messages

**Example**:
```bash
uv run main.py team
# Output: Formatted table of team members
```

---

##### `specify(prompt: str, db_name: str = "master", collection_name: str = "llm")`

**Description**: Generates a specification schema using LLM and stores it in MongoDB.

**Parameters**:
- `prompt` (str): User prompt to send to the LLM
- `db_name` (str, optional): Target database name. Defaults to "master"
- `collection_name` (str, optional): Target collection name. Defaults to "llm"

**Returns**: None (prints to console and stores in database)

**Behavior**:
1. Creates FireworksClient instance
2. Generates structured response using SpecifySchema
3. Parses JSON response
4. Inserts document into MongoDB
5. Displays generated schema with syntax highlighting

**Error Handling**:
- Catches JSON parsing errors
- Catches general exceptions
- Displays errors using Rich console

**Example**:
```bash
uv run main.py specify "Create a user authentication system"
```

---

## Database Module (`src/db/`)

### `client.py`

#### Class: `MongoDBClient`

**Description**: MongoDB client wrapper with context manager support for automatic connection management.

**Constructor**:
```python
def __init__(self, connection_string: Optional[str] = None)
```

**Parameters**:
- `connection_string` (str, optional): MongoDB connection URI. Reads from `MONGODB_URI` env var if not provided

**Methods**:

##### `__enter__()`

**Description**: Context manager entry point.

**Returns**: `self` (MongoDBClient instance)

**Behavior**: Enables `with` statement usage for automatic connection management

---

##### `__exit__(exc_type, exc_val, exc_tb)`

**Description**: Context manager exit point.

**Parameters**:
- `exc_type`: Exception type (if any)
- `exc_val`: Exception value (if any)
- `exc_tb`: Exception traceback (if any)

**Returns**: None

**Behavior**: Closes MongoDB connection automatically

---

##### `get_database(db_name: str)`

**Description**: Returns a database instance.

**Parameters**:
- `db_name` (str): Name of the database to access

**Returns**: MongoDB database instance

---

### `operations.py`

Contains generic CRUD operations for MongoDB collections.

#### Function: `upsert_document()`

```python
def upsert_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any],
    document: Dict[str, Any],
    upsert: bool = True
) -> Any
```

**Description**: Updates an existing document or inserts a new one if not found.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `query`: Query to find existing document
- `document`: Document data to insert/update
- `upsert`: Insert if not found (default: True)

**Returns**: MongoDB update result

---

#### Function: `get_document()`

```python
def get_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> Optional[Dict[str, Any]]
```

**Description**: Retrieves a single document matching the query.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `query`: Query criteria

**Returns**: Document dict if found, None otherwise

---

#### Function: `get_documents()`

```python
def get_documents(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any],
    limit: Optional[int] = None,
    sort: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]
```

**Description**: Retrieves multiple documents matching the query.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `query`: Query criteria
- `limit`: Maximum documents to return (optional)
- `sort`: List of (field, direction) tuples for sorting (optional)

**Returns**: List of document dicts

---

#### Function: `insert_document()`

```python
def insert_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    document: Dict[str, Any]
) -> Any
```

**Description**: Inserts a single document into the collection.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `document`: Document to insert

**Returns**: Inserted document ID

---

#### Function: `insert_documents()`

```python
def insert_documents(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    documents: List[Dict[str, Any]]
) -> List[Any]
```

**Description**: Inserts multiple documents into the collection.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `documents`: List of documents to insert

**Returns**: List of inserted document IDs

---

#### Function: `delete_document()`

```python
def delete_document(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> int
```

**Description**: Deletes a single document matching the query.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `query`: Query criteria

**Returns**: Number of documents deleted (0 or 1)

---

#### Function: `delete_documents()`

```python
def delete_documents(
    db_client: MongoDBClient,
    db_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> int
```

**Description**: Deletes multiple documents matching the query.

**Parameters**:
- `db_client`: MongoDBClient instance
- `db_name`: Database name
- `collection_name`: Collection name
- `query`: Query criteria

**Returns**: Number of documents deleted

---

## LLM Module (`src/llm/`)

### `client.py`

#### Class: `FireworksClient`

**Description**: Client for interacting with Fireworks AI LLM services.

**Constructor**:
```python
def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-v3p1-terminus")
```

**Parameters**:
- `api_key` (str, optional): Fireworks API key. Reads from `FIREWORKS_API_KEY` env var if not provided
- `model` (str): Model name. Defaults to "deepseek-v3p1-terminus"

**Raises**:
- `ValueError`: If API key is not provided and not found in environment

**Attributes**:
- `api_key`: API key for authentication
- `model`: Model identifier
- `_client`: Internal LLM client instance

---

##### `generate_with_schema()`

```python
def generate_with_schema(
    self,
    prompt: str,
    schema: Dict[str, Any],
    schema_name: str = "ResponseSchema"
) -> str
```

**Description**: Generates a response following a specific JSON schema using structured output.

**Parameters**:
- `prompt`: User prompt to send to the LLM
- `schema`: Pydantic model JSON schema to enforce
- `schema_name`: Name of the schema (default: "ResponseSchema")

**Returns**: Generated response content as a JSON string

**Behavior**:
- Enforces JSON schema compliance in LLM output
- Uses chat completions API with schema enforcement
- Returns structured JSON response

**Example**:
```python
client = FireworksClient()
response = client.generate_with_schema(
    prompt="Describe a user",
    schema=UserSchema.model_json_schema(),
    schema_name="UserSchema"
)
```

---

##### `chat()`

```python
def chat(
    self,
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str
```

**Description**: Simple chat completion without schema enforcement.

**Parameters**:
- `messages`: List of message dicts with 'role' and 'content' keys
- `temperature`: Sampling temperature (default: 0.7)
- `max_tokens`: Maximum tokens to generate (default: 2000)

**Returns**: Generated response content as a string

**Example**:
```python
client = FireworksClient()
response = client.chat(
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

---

### `embeddings.py`

#### Class: `VoyageEmbeddings`

**Description**: Client for generating embeddings using Voyage AI.

**Constructor**:
```python
def __init__(self, api_key: Optional[str] = None, model: str = "voyage-2")
```

**Parameters**:
- `api_key` (str, optional): Voyage API key. Reads from `VOYAGE_API_KEY` env var if not provided
- `model` (str): Model name. Defaults to "voyage-2"

**Attributes**:
- `api_key`: API key for authentication
- `model`: Model identifier
- `default_dimension`: Default embedding dimension (1024 for voyage-2)

---

##### `embed()`

```python
def embed(self, text: str) -> List[float]
```

**Description**: Generates embedding vector for a single text.

**Parameters**:
- `text`: Text to embed

**Returns**: List of floats representing the embedding (real embeddings from API or dummy vector if API unavailable)

**Behavior**:
- Makes API call to Voyage AI
- Returns 1024-dimensional vector
- Gracefully handles errors with dummy embeddings
- Timeout: 30 seconds

**Error Handling**:
- Returns dummy embeddings if API key not set
- Returns dummy embeddings on API failure
- Prints warning message on failure

---

##### `embed_batch()`

```python
def embed_batch(self, texts: List[str]) -> List[List[float]]
```

**Description**: Generates embeddings for multiple texts in a single API call.

**Parameters**:
- `texts`: List of texts to embed

**Returns**: List of embedding vectors corresponding to input texts (one vector per input text, using real or dummy embeddings)

**Behavior**:
- Batch processing for efficiency
- Same error handling as `embed()`
- Timeout: 30 seconds

---

### `segmentation.py`

#### Class: `SpecificationSegmenter`

**Description**: Segments natural language prompts into atomic memory specifications using LLM.

**Constructor**:
```python
def __init__(self, api_key: str = None, model: str = None)
```

**Parameters**:
- `api_key` (str, optional): Fireworks API key. Reads from `FIREWORKS_API_KEY` env var if not provided
- `model` (str, optional): Model identifier. Reads from `FIREWORKS_MODEL` env var or defaults to "accounts/fireworks/models/llama-v3p1-70b-instruct"

**Attributes**:
- `api_key`: API key for authentication
- `model`: Model identifier for Fireworks AI

**Constants**:
- `LLM_SYSTEM_PROMPT`: System prompt that instructs the LLM to convert prompts into structured memories
- `FALLBACK_MEMORIES`: Example JSONL memories used when API is unavailable

---

##### `segment_to_jsonl()`

```python
def segment_to_jsonl(self, prompt_text: str, tags: List[str]) -> str
```

**Description**: Segments a specification prompt into JSONL-formatted memories using Fireworks AI LLM.

**Parameters**:
- `prompt_text`: The specification prompt to segment
- `tags`: List of suggested tags for the LLM to use

**Returns**: JSONL string containing segmented memories

**Memory Fields**:
- `kind`: Type of memory (vibe, spec, constraint, non_goal, metric, example, open_question)
- `title`: Short title for the memory
- `content`: Content (≤ 8 lines)
- `tags`: List of tags
- `deps`: List of dependencies

**Behavior**:
- Sends prompt to Fireworks AI with system instructions
- Returns structured JSONL output
- Falls back to example memories if API unavailable
- Temperature: 0.7, Max tokens: 2000, Timeout: 30s

**Error Handling**:
- Returns `FALLBACK_MEMORIES` if API key not set
- Returns fallback memories on API failure
- Prints warning message on errors

**Example**:
```python
segmenter = SpecificationSegmenter()
jsonl = segmenter.segment_to_jsonl(
    prompt_text="Create a photo album app with drag and drop",
    tags=["photos", "albums", "ux"]
)
```

---

##### `parse_jsonl()`

```python
def parse_jsonl(self, jsonl_text: str) -> List[Dict]
```

**Description**: Parses JSONL text into a list of dictionaries.

**Parameters**:
- `jsonl_text`: JSONL formatted string (one JSON object per line)

**Returns**: List of parsed JSON objects

**Behavior**:
- Splits text by newlines
- Parses each non-empty line as JSON
- Skips invalid lines with warning
- Continues parsing after errors

**Error Handling**:
- Catches `JSONDecodeError` for individual lines
- Prints warning for failed lines
- Continues processing remaining lines

**Example**:
```python
segmenter = SpecificationSegmenter()
jsonl = '''{"kind": "spec", "title": "Feature A", "content": "...", "tags": [], "deps": []}
{"kind": "constraint", "title": "Limit B", "content": "...", "tags": [], "deps": []}'''
memories = segmenter.parse_jsonl(jsonl)
# Returns: [{"kind": "spec", ...}, {"kind": "constraint", ...}]
```

---

## Schemas Module (`src/schemas/`)

### `models.py`

Contains Pydantic models for data validation.

#### Class: `DecayModel`

**Description**: Model for memory decay parameters.

**Fields**:
- `lambda_` (float): Decay rate parameter (aliased from "lambda")
- `pinned` (bool): Whether memory is pinned (no decay)

**Configuration**:
- Uses field alias for Python keyword compatibility
- `populate_by_name = True`: Allows both "lambda" and "lambda_"

---

#### Class: `MetadataModel`

**Description**: Model for memory metadata.

**Fields**:
- `source` (str): Source identifier
- `content_hash` (str): Hash of content for deduplication

---

#### Class: `SpecifySchema`

**Description**: Main schema for specification/memory documents.

**Fields**:
- `memory_id` (str): Unique memory identifier
- `project_id` (str): Associated project ID
- `created_at` (str): ISO 8601 datetime string
- `author` (str): Document author
- `kind` (str): Type of specification
- `title` (str): Document title
- `content` (str): Main content
- `tags` (List[str]): Associated tags
- `deps` (List[str]): Dependencies (linked memory IDs)
- `priority` (float): Priority score
- `decay` (DecayModel): Decay parameters
- `metadata` (MetadataModel): Document metadata
- `embedding` (Optional[List[float]]): Vector embedding (optional)

**Configuration**:
- `populate_by_name = True`: Flexible field naming
- `arbitrary_types_allowed = True`: Allows complex types
- Custom JSON encoder for ObjectId types

**Usage**:
```python
schema = SpecifySchema(
    memory_id="mem_123",
    project_id="proj_456",
    created_at="2025-10-16T15:42:00Z",
    author="user@example.com",
    kind="requirement",
    title="User Authentication",
    content="System shall support user login...",
    tags=["auth", "security"],
    deps=[],
    priority=1.0,
    decay=DecayModel(lambda_=0.1, pinned=False),
    metadata=MetadataModel(
        source="spec-kit",
        content_hash="abc123..."
    )
)
```

---

## Entry Point (`main.py`)

### Module-Level Code

```python
if __name__ == "__main__":
    app()
```

**Description**: Entry point that runs the Typer CLI application.

**Behavior**:
- Imports the Typer app from `src.cli`
- Executes CLI commands based on command-line arguments

---

## Common Usage Patterns

### Database Operations

```python
# Query documents
with MongoDBClient() as db_client:
    docs = get_documents(
        db_client=db_client,
        db_name="master",
        collection_name="team",
        query={"status": "active"}
    )

# Insert document
with MongoDBClient() as db_client:
    doc_id = insert_document(
        db_client=db_client,
        db_name="master",
        collection_name="notes",
        document={"title": "Example", "content": "..."}
    )
```

### LLM Integration

```python
# Schema-enforced generation
llm_client = FireworksClient()
response = llm_client.generate_with_schema(
    prompt="Generate a specification...",
    schema=SpecifySchema.model_json_schema(),
    schema_name="SpecifySchema"
)
doc = json.loads(response)

# Simple chat
response = llm_client.chat(
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Embeddings

```python
# Single text embedding
embedder = VoyageEmbeddings()
vector = embedder.embed("Sample text to embed")

# Batch embedding
vectors = embedder.embed_batch([
    "First text",
    "Second text",
    "Third text"
])
```

### Specification Segmentation

```python
# Segment prompt into atomic memories
segmenter = SpecificationSegmenter()
jsonl = segmenter.segment_to_jsonl(
    prompt_text="Build a photo sharing app with albums",
    tags=["photos", "albums", "ux"]
)

# Parse JSONL to list of memories
memories = segmenter.parse_jsonl(jsonl)

# Process each memory
for memory in memories:
    print(f"{memory['kind']}: {memory['title']}")
```

---

## Type Hints and Type Safety

All modules use type hints extensively:
- Function parameters and return types are annotated
- Pydantic models provide runtime validation
- Optional types use `Optional[T]` or `T | None`
- Collections use `List[T]`, `Dict[K, V]`, etc.

This ensures:
- Better IDE support (autocomplete, type checking)
- Clearer documentation
- Runtime validation via Pydantic
- Easier refactoring and maintenance
