# LLM Usage

## Overview

Vibe Engineering integrates Large Language Models (LLMs) to provide intelligent specification generation and semantic search capabilities. The system uses two primary AI services:

1. **Fireworks AI** - For text generation and structured output
2. **Voyage AI** - For text embeddings and semantic search

This document describes how LLMs are integrated, configured, and used throughout the application.

---

## Fireworks AI Integration

### Overview

Fireworks AI provides the LLM capabilities for generating structured specifications and chat completions. The system uses the `deepseek-v3p1-terminus` model by default.

### Client: `FireworksClient`

Located in `src/llm/client.py`, this class wraps the Fireworks AI API.

#### Configuration

**Environment Variable**: `FIREWORKS_API_KEY`

```bash
# In .env file
FIREWORKS_API_KEY=your_api_key_here
```

**Initialization**:
```python
from src.llm import FireworksClient

# Uses environment variable
client = FireworksClient()

# Or provide API key directly
client = FireworksClient(api_key="your_key", model="deepseek-v3p1-terminus")
```

### Use Cases

#### 1. Structured Output Generation

The primary use case is generating structured specifications that conform to a specific schema.

**Method**: `generate_with_schema()`

**How It Works**:
1. Accepts a user prompt describing what to generate
2. Takes a Pydantic model's JSON schema as a constraint
3. Forces the LLM to output valid JSON matching the schema
4. Returns structured data that can be validated and stored

**Example - Specification Generation**:

```python
from src.llm import FireworksClient
from src.schemas import SpecifySchema
import json

# Initialize client
llm_client = FireworksClient()

# Generate structured specification
prompt = """
Create a specification for a user authentication system with the following:
- Email/password login
- OAuth2 support
- Password reset functionality
- Two-factor authentication
"""

response = llm_client.generate_with_schema(
    prompt=prompt,
    schema=SpecifySchema.model_json_schema(),
    schema_name="SpecifySchema"
)

# Parse and validate
spec = json.loads(response)
validated_spec = SpecifySchema(**spec)
```

**Benefits**:
- **Type Safety**: Output always matches the schema
- **Validation**: Automatic validation through Pydantic
- **Predictability**: No need for complex parsing or error handling
- **Storage Ready**: Can be directly inserted into MongoDB

#### 2. Unstructured Chat Completions

For more flexible interactions without schema constraints.

**Method**: `chat()`

**Example**:
```python
client = FireworksClient()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain dependency injection"}
]

response = client.chat(
    messages=messages,
    temperature=0.7,
    max_tokens=2000
)

print(response)
```

**Parameters**:
- `messages`: Conversation history (list of role/content dicts)
- `temperature`: Creativity level (0.0 = deterministic, 1.0 = creative)
- `max_tokens`: Maximum response length

### CLI Integration: `specify` Command

The `specify` command demonstrates the complete workflow:

```bash
uv run main.py specify "Create a payment processing system"
```

**Workflow**:
1. User provides natural language prompt
2. `FireworksClient` generates structured specification
3. JSON response is parsed and validated
4. Document is stored in MongoDB
5. Pretty-printed output shown to user

**Code Flow**:
```python
@app.command()
def specify(prompt: str, db_name: str = "master", collection_name: str = "llm"):
    # 1. Generate with schema
    llm_client = FireworksClient()
    response = llm_client.generate_with_schema(
        prompt=prompt,
        schema=SpecifySchema.model_json_schema(),
        schema_name="SpecifySchema",
    )
    
    # 2. Parse JSON
    doc = json.loads(response)
    
    # 3. Store in database
    with MongoDBClient() as db_client:
        inserted_id = insert_document(
            db_client=db_client,
            db_name=db_name,
            collection_name=collection_name,
            document=doc
        )
    
    # 4. Display results
    console.print(f"[green]✓[/green] Document stored")
    console.print(Syntax(json.dumps(doc, indent=2), "json"))
```

---

## Voyage AI Integration

### Overview

Voyage AI provides embedding generation for semantic search and similarity matching. The system uses the `voyage-2` model which produces 1024-dimensional vectors.

### Client: `VoyageEmbeddings`

Located in `src/llm/embeddings.py`, this class wraps the Voyage AI API.

#### Configuration

**Environment Variable**: `VOYAGE_API_KEY`

```bash
# In .env file
VOYAGE_API_KEY=your_api_key_here
```

**Initialization**:
```python
from src.llm import VoyageEmbeddings

# Uses environment variable
embedder = VoyageEmbeddings()

# Or provide API key directly
embedder = VoyageEmbeddings(api_key="your_key", model="voyage-2")
```

### Use Cases

#### 1. Single Text Embedding

Generate a vector representation for a single piece of text.

**Method**: `embed()`

**Example**:
```python
embedder = VoyageEmbeddings()

text = "User authentication system with OAuth2 support"
vector = embedder.embed(text)

# vector is a List[float] with 1024 dimensions
print(f"Embedding dimension: {len(vector)}")  # 1024
```

**Use Cases**:
- Embed user queries for semantic search
- Generate embeddings for new documents
- Compare similarity between texts

#### 2. Batch Embedding

Process multiple texts efficiently in a single API call.

**Method**: `embed_batch()`

**Example**:
```python
embedder = VoyageEmbeddings()

texts = [
    "Authentication and authorization",
    "Database schema design",
    "API endpoint implementation",
    "Frontend user interface"
]

vectors = embedder.embed_batch(texts)

# vectors is List[List[float]], one vector per input text
print(f"Generated {len(vectors)} embeddings")
```

**Benefits**:
- **Efficiency**: Single API call for multiple texts
- **Rate Limit Friendly**: Reduces number of requests
- **Consistent**: All embeddings generated with same model state

#### 3. Graceful Degradation

The embedding client handles missing API keys gracefully:

```python
# Without API key
embedder = VoyageEmbeddings()  # VOYAGE_API_KEY not set

# Still returns dummy embeddings for testing
vector = embedder.embed("test text")
# Returns [0.0, 0.0, ..., 0.0] (1024 zeros)
```

**Error Handling**:
- Missing API key → returns dummy embeddings
- API failure → prints warning, returns dummy embeddings
- Timeout (30s) → falls back to dummy embeddings

### Integration with MongoDB

Embeddings are stored in MongoDB documents for vector search:

```python
from src.llm import VoyageEmbeddings
from src.db import MongoDBClient, insert_document

embedder = VoyageEmbeddings()

# Generate embedding
text = "Create a REST API for user management"
vector = embedder.embed(text)

# Store with document
document = {
    "title": "User Management API Spec",
    "content": text,
    "embedding": vector,  # List[float] stored directly
    "project_id": "proj_123",
    "type": "requirement"
}

with MongoDBClient() as db_client:
    insert_document(
        db_client=db_client,
        db_name="master",
        collection_name="notes",
        document=document
    )
```

### Vector Search

MongoDB Atlas Vector Search can query similar documents:

```python
# Pseudo-code for vector search
query_text = "user authentication system"
query_vector = embedder.embed(query_text)

pipeline = [
    {
        "$search": {
            "index": "notes_vec",
            "knnBeta": {
                "vector": query_vector,
                "path": "embedding",
                "k": 10  # Return top 10 similar documents
            }
        }
    },
    {"$limit": 10}
]

results = db.notes.aggregate(pipeline)
```

---

## LLM Best Practices

### 1. Schema-Driven Design

**Always use schemas for structured output**:
```python
# Good - Structured output
response = client.generate_with_schema(
    prompt=prompt,
    schema=SpecifySchema.model_json_schema(),
    schema_name="SpecifySchema"
)

# Avoid - Unstructured parsing
response = client.chat([{"role": "user", "content": prompt}])
# Now need to parse JSON manually with error handling
```

### 2. Prompt Engineering

**Be specific and provide context**:

```python
# Good - Specific and contextual
prompt = """
Create a technical specification for an authentication system with:
- Requirements: OAuth2, 2FA, password reset
- Tech stack: Python FastAPI, MongoDB
- Security: OWASP compliance
- Include: acceptance criteria, edge cases, error handling
"""

# Weak - Vague
prompt = "Make an auth system"
```

### 3. Error Handling

**Always handle LLM failures gracefully**:

```python
try:
    response = llm_client.generate_with_schema(
        prompt=prompt,
        schema=schema,
        schema_name="Schema"
    )
    doc = json.loads(response)
except json.JSONDecodeError as e:
    console.print(f"[red]Invalid JSON from LLM:[/red] {e}")
except Exception as e:
    console.print(f"[red]LLM error:[/red] {e}")
```

### 4. Embedding Strategy

**Embed meaningful content, not raw code**:

```python
# Good - Semantic summary
summary = f"{doc['title']}: {doc['content'][:500]}"
vector = embedder.embed(summary)

# Avoid - Raw code
vector = embedder.embed(entire_codebase)  # Too specific, poor recall
```

### 5. Batch When Possible

**Use batch operations for efficiency**:

```python
# Good - Single API call
all_texts = [doc["content"] for doc in documents]
all_vectors = embedder.embed_batch(all_texts)

# Wasteful - Multiple calls
all_vectors = [embedder.embed(doc["content"]) for doc in documents]
```

---

## Advanced Usage Patterns

### 1. Hybrid Search

Combine vector search with filters for precise results:

```python
query_vector = embedder.embed("user authentication")

pipeline = [
    {
        "$search": {
            "compound": {
                "must": [
                    {
                        "knnBeta": {
                            "vector": query_vector,
                            "path": "embedding",
                            "k": 20
                        }
                    }
                ],
                "filter": [
                    {"equals": {"path": "project_id", "value": "proj_123"}},
                    {"equals": {"path": "type", "value": "requirement"}}
                ]
            }
        }
    }
]
```

### 2. Multi-Stage LLM Pipeline

Chain LLM calls for complex workflows:

```python
# Stage 1: Generate requirements
requirements = llm_client.generate_with_schema(
    prompt="Create requirements for a payment system",
    schema=RequirementSchema.model_json_schema(),
    schema_name="Requirements"
)

# Stage 2: Generate design from requirements
design = llm_client.generate_with_schema(
    prompt=f"Create technical design for: {requirements}",
    schema=DesignSchema.model_json_schema(),
    schema_name="Design"
)

# Stage 3: Generate tasks from design
tasks = llm_client.generate_with_schema(
    prompt=f"Break down into tasks: {design}",
    schema=TaskSchema.model_json_schema(),
    schema_name="Tasks"
)
```

### 3. Memory-Augmented Generation

Use embeddings to retrieve relevant context:

```python
# Retrieve relevant memories
query_vector = embedder.embed(user_prompt)
relevant_docs = vector_search(query_vector, limit=5)

# Augment prompt with context
context = "\n".join([doc["content"] for doc in relevant_docs])
augmented_prompt = f"""
Context from previous specifications:
{context}

New request: {user_prompt}
"""

# Generate with context
response = llm_client.generate_with_schema(
    prompt=augmented_prompt,
    schema=schema,
    schema_name="Schema"
)
```

---

## Performance Considerations

### API Costs

**Fireworks AI**:
- Charged per token (input + output)
- Schema enforcement may increase output tokens slightly
- Use appropriate `max_tokens` limits

**Voyage AI**:
- Charged per text embedded
- Batch processing doesn't reduce cost but improves throughput
- 1024-dimensional vectors for voyage-2 model

### Rate Limits

- Implement exponential backoff for rate limit errors
- Use batch operations to reduce request count
- Cache embeddings when possible (they're deterministic)

### Timeouts

Current timeout settings:
- **Voyage AI**: 30 seconds per request
- **Fireworks AI**: Uses SDK defaults

Consider adjusting based on:
- Prompt complexity
- Expected response length
- Network conditions

### Optimization Tips

1. **Cache embeddings**: Same text always produces same vector
2. **Batch operations**: Reduce API overhead
3. **Limit prompt length**: Shorter prompts = faster responses
4. **Appropriate model selection**: Balance capability vs. cost
5. **Schema simplification**: Smaller schemas = faster generation

---

## Future Enhancements

### Planned Features

1. **Multi-Model Support**: 
   - Support multiple LLM providers (OpenAI, Anthropic, etc.)
   - Provider abstraction layer
   - Fallback providers for reliability

2. **Async Operations**:
   - Non-blocking LLM calls
   - Concurrent batch processing
   - Background embedding generation

3. **Caching Layer**:
   - Redis cache for embeddings
   - LLM response caching for repeated queries
   - Cache invalidation strategies

4. **Advanced RAG**:
   - Reranking retrieved documents
   - Query expansion
   - Multi-query retrieval

5. **Monitoring**:
   - LLM call metrics (latency, cost, success rate)
   - Embedding generation tracking
   - Quality metrics for generated content

---

## Troubleshooting

### Common Issues

#### "FIREWORKS_API_KEY environment variable is not set"

**Solution**: Add API key to `.env` file:
```bash
cp .env.dist .env
# Edit .env and add: FIREWORKS_API_KEY=your_key_here
```

#### Embeddings return all zeros

**Cause**: Voyage API key not set or API failure

**Impact**: Minimal - allows testing without API access

**Solution**: Set `VOYAGE_API_KEY` in `.env` for production use

#### JSON parsing errors from LLM

**Cause**: Schema too complex or prompt unclear

**Solution**:
- Simplify the schema
- Make prompt more specific
- Add example output in prompt
- Retry with different temperature

#### Slow LLM responses

**Causes**:
- Complex schema
- Long prompt
- Network latency

**Solutions**:
- Reduce `max_tokens`
- Simplify schema
- Use streaming (future feature)

---

## Security Considerations

### API Key Management

- **Never commit API keys** to version control
- Use `.env` files (excluded in `.gitignore`)
- Rotate keys regularly
- Use separate keys for development/production

### Input Validation

- Always validate user prompts before sending to LLM
- Sanitize LLM outputs before storing in database
- Set reasonable length limits on prompts

### Output Validation

- Schema enforcement provides first layer of validation
- Always validate with Pydantic models
- Check for injection attempts in generated content
- Sanitize before rendering to users

### Rate Limiting

- Implement rate limiting for user-facing commands
- Monitor usage to detect abuse
- Set budget alerts on LLM providers

---

## Monitoring and Observability

### Metrics to Track

1. **LLM Performance**:
   - Average response time
   - Success/failure rate
   - Token usage per request
   - Cost per operation

2. **Embedding Quality**:
   - Embedding generation time
   - Batch size distribution
   - Cache hit rate

3. **User Behavior**:
   - Commands used most frequently
   - Prompt characteristics
   - Specification types generated

### Logging

Currently uses console output. Consider adding:
- Structured logging (JSON format)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging (with PII redaction)
- Error tracking integration

---

## Resources

### Documentation Links

- **Fireworks AI**: https://docs.fireworks.ai/
- **Voyage AI**: https://docs.voyageai.com/
- **Pydantic**: https://docs.pydantic.dev/
- **MongoDB Vector Search**: https://www.mongodb.com/docs/atlas/atlas-vector-search/

### Related Files

- `src/llm/client.py` - Fireworks AI client implementation
- `src/llm/embeddings.py` - Voyage AI embeddings client
- `src/schemas/models.py` - Pydantic schemas for structured output
- `src/cli/commands.py` - CLI commands using LLMs
- `docs/high-level-design.md` - System design overview
