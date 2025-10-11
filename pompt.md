# VoyageAI Integration for Spec-Kit CLI Project

## Context
You are working on a Python CLI project that replicates the functionality of github/spec-kit. The project needs to integrate VoyageAI embeddings with MongoDB for vector search capabilities.

## Objective
Add VoyageAI integration to the existing CLI project with the following requirements:

### 1. VoyageAI Connection Setup
- Add VoyageAI client initialization using the `voyageai` Python SDK
- Support API key configuration through:
  - Environment variable (`VOYAGE_API_KEY`)
  - Configuration file
  - CLI argument (for testing purposes)
- Implement connection validation and error handling
- Use appropriate VoyageAI embedding models (e.g., `voyage-code-2` for code embeddings)

### 2. MongoDB Vector Search Integration
- Configure MongoDB connection with vector search capabilities
- Create appropriate collection schema for storing:
  - Document content (specification text/code)
  - VoyageAI embeddings (vector field)
  - Metadata (file path, timestamp, tags)
- Implement vector index creation for efficient similarity search
- Use MongoDB's `$vectorSearch` aggregation stage

### 3. CLI Command for Testing Connection
Create a new CLI command: `test-connection` (or similar) that:
- Tests VoyageAI API connectivity
- Validates API key is working
- Generates a sample embedding from test text
- Tests MongoDB connection
- Verifies vector index exists/is accessible
- Provides clear success/failure feedback with helpful error messages
- Shows connection latency/performance metrics

Example command usage:
```bash
# Test both connections
python cli.py test-connection

# Test only VoyageAI
python cli.py test-connection --service voyageai

# Test only MongoDB
python cli.py test-connection --service mongodb

# Verbose output
python cli.py test-connection --verbose
```

### 4. Technical Requirements
- Use Python's `click` or `argparse` for CLI commands
- Implement proper logging with different verbosity levels
- Add appropriate exception handling for:
  - Network errors
  - Authentication failures
  - Invalid configurations
  - MongoDB connection issues
- Include helpful error messages that guide users to solutions
- Follow the existing project structure and coding conventions

### 5. Configuration Structure
Create or update configuration to include:
```python
{
    "voyageai": {
        "api_key": "your-api-key",
        "model": "voyage-code-2",
        "batch_size": 128
    },
    "mongodb": {
        "uri": "mongodb://localhost:27017",
        "database": "speckit",
        "collection": "specifications",
        "vector_index": "spec_vector_index"
    }
}
```

### 6. Testing Output Format
The test command should output:
- ✓/✗ status indicators
- Connection timing
- API version/model information
- Any warnings or recommendations
- Sample embedding dimensions

### 7. Code Organization
- Create separate modules for:
  - `voyageai_client.py` - VoyageAI wrapper
  - `mongodb_client.py` - MongoDB connection and operations
  - `commands/test_connection.py` - CLI test command
- Keep existing project structure intact
- Add new dependencies to `requirements.txt` or `pyproject.toml`

## Dependencies to Add
```
voyageai>=0.2.0
pymongo>=4.0.0
python-dotenv>=1.0.0
```

## Expected Deliverables
1. VoyageAI client wrapper with connection management
2. MongoDB vector search configuration
3. CLI command for connection testing
4. Updated configuration handling
5. Error handling and logging
6. Basic documentation/docstrings

## Success Criteria
- User can run `test-connection` and verify both services are working
- Clear error messages when connections fail
- Proper configuration management
- Code follows existing project patterns
- No breaking changes to existing functionality