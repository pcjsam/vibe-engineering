# Architecture

## Overview

Vibe Engineering is a memory-backed specification toolkit built with Python. It uses agentic memory principles to maintain structured, queryable context for development workflows, improving build reliability, code quality, and architectural consistency.

## Technology Stack

### Core Technologies

- **Language**: Python 3.13
- **CLI Framework**: Typer (type-safe command-line interface)
- **Database**: MongoDB Atlas (document-first, schema via Pydantic models)
- **Package Manager**: uv (fast Python package installer)
- **Environment Management**: python-dotenv for configuration

### Key Dependencies

- **typer**: CLI framework for building command-line applications
- **rich**: Terminal formatting and beautiful output
- **pymongo**: MongoDB driver for Python
- **pydantic**: Data validation using Python type annotations
- **fireworks-ai**: LLM integration for Fireworks AI
- **requests**: HTTP library for API calls (used for Voyage embeddings)

## System Architecture

### High-Level Design

The system follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│         CLI Layer (Typer)           │
│   - Commands (hello, goodbye, etc)  │
│   - User interaction                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Application Layer             │
│   - Business logic                   │
│   - Data transformation              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Integration Layer              │
│  ┌─────────────┐  ┌────────────┐   │
│  │ DB Module   │  │ LLM Module │   │
│  │ (MongoDB)   │  │ (Fireworks)│   │
│  └─────────────┘  └────────────┘   │
└─────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      External Services               │
│  - MongoDB Atlas                     │
│  - Fireworks AI API                  │
│  - Voyage AI API                     │
└─────────────────────────────────────┘
```

### Module Structure

```
vibe-engineering/
├── main.py                 # Entry point
├── src/
│   ├── cli/               # CLI commands and interface
│   │   ├── __init__.py
│   │   └── commands.py    # Typer commands
│   ├── db/                # Database layer
│   │   ├── __init__.py
│   │   ├── client.py      # MongoDB client
│   │   └── operations.py  # CRUD operations
│   ├── llm/               # LLM integration layer
│   │   ├── __init__.py
│   │   ├── client.py      # Fireworks AI client
│   │   ├── embeddings.py  # Voyage embeddings
│   │   └── segmentation.py
│   └── schemas/           # Data models
│       ├── __init__.py
│       └── models.py      # Pydantic models
└── docs/                  # Documentation
```

## Data Architecture

### MongoDB Collections

Based on the design documents, the system uses these collections:

- **projects**: Project metadata (`_id`, `slug`, `repo_url`, `created_at`, `owners`)
- **notes**: Structured notes with embeddings (`_id`, `project_id`, `type`, `title`, `text`, `fields`, `links`, `tags`, `embedding`)
- **edges**: Relationships between notes (`_id`, `src_id`, `dst_id`, `rel`)
- **facts**: Immutable events (`_id`, `project_id`, `kind`, `payload`, `ts`)
- **team**: Team member information
- **llm**: LLM-generated specifications

### Data Model

The system uses Pydantic models for data validation:

- **SpecifySchema**: Main schema for specification/memory documents
- **DecayModel**: Memory decay parameters
- **MetadataModel**: Document metadata (source, content hash)

## Design Patterns

### 1. Context Manager Pattern

MongoDB client uses context manager for automatic resource cleanup:

```python
with MongoDBClient() as db_client:
    # Database operations
    pass
```

### 2. Client Pattern

Separate clients for different services:
- `MongoDBClient`: Database operations
- `FireworksClient`: LLM interactions
- `VoyageEmbeddings`: Embedding generation

### 3. Repository Pattern

Database operations abstracted through generic CRUD functions in `operations.py`:
- `insert_document()`, `get_document()`, `get_documents()`
- `upsert_document()`, `delete_document()`, `delete_documents()`

### 4. Schema-Driven Design

Uses Pydantic models for:
- Data validation
- JSON schema generation for LLM responses
- Type safety across the application

## Architectural Principles

### 1. Separation of Concerns

- **CLI Layer**: User interaction and command routing
- **Application Layer**: Business logic and orchestration
- **Data Layer**: Persistence and retrieval
- **Integration Layer**: External service communication

### 2. Memory as Source of Truth

Following the spec-kit philosophy:
- Structured notes stored in MongoDB serve as the source of truth
- Markdown files are generated views for human review
- Embeddings enable semantic retrieval
- Graph relationships track traceability

### 3. Type Safety

- Pydantic models ensure data validation
- Type hints throughout the codebase
- Schema enforcement for LLM responses

### 4. Async-Ready Design

While current implementation is synchronous, the architecture supports:
- MongoDB operations through Motor (async driver)
- FastAPI backend for async endpoints (future consideration)

## Configuration Management

### Environment Variables

The system uses `.env` files for configuration:

```bash
MONGODB_URI=mongodb+srv://...
FIREWORKS_API_KEY=...
VOYAGE_API_KEY=...
```

### Configuration Flow

1. Load environment variables via `python-dotenv`
2. Pass to client constructors
3. Validate required credentials at runtime

## Error Handling

### Strategy

- Graceful degradation for optional services (e.g., embeddings return dummy values if API key missing)
- Rich console output for user-friendly error messages
- Exception handling at command level to prevent crashes

## Scalability Considerations

### Current State

- Synchronous operations suitable for CLI use cases
- MongoDB Atlas provides scalable document storage
- Vector search capabilities for semantic retrieval

### Future Enhancements

- Async operations for concurrent processing
- Caching layer for frequently accessed data
- Batch processing for bulk operations
- FastAPI backend for web interface

## Security

### Current Measures

1. **Credential Management**: API keys stored in environment variables
2. **Validation**: Pydantic models validate all input data
3. **Database Access**: Connection strings kept in `.env` files

### Best Practices

- Never commit `.env` files (included in `.gitignore`)
- Use least-privilege database credentials
- Validate and sanitize all user inputs
- Safe defaults for optional parameters

## Testing Strategy

While no tests currently exist, the architecture supports:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test database and LLM interactions
- **CLI Tests**: Test command execution and output
- **Mocking**: External services can be mocked for testing

## Development Workflow

### Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.dist .env
# Edit .env with real credentials

# Run CLI
uv run main.py <command> <args>
```

### Adding New Features

1. Define Pydantic models in `src/schemas/`
2. Implement business logic in respective modules
3. Create CLI commands in `src/cli/commands.py`
4. Update documentation

## Performance Considerations

### Database

- MongoDB indexes on frequently queried fields
- Vector search index on embeddings
- Pagination for large result sets

### LLM Integration

- Schema-enforced responses reduce parsing errors
- Timeout configurations for API calls
- Graceful fallbacks for API failures

### Memory Management

- Context manager pattern ensures resource cleanup
- Connection pooling via MongoDB client
- Lazy loading where appropriate
