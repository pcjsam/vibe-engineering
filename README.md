# Spec-Kit CLI with VoyageAI Integration

A Python CLI tool that replicates the functionality of github/spec-kit with VoyageAI embeddings and MongoDB vector search capabilities.

## Requirements

- Python 3.13+
- uv (or pip)
- Git
- MongoDB (for vector search)
- VoyageAI API key

## Installation

1. Install dependencies

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## Configuration

1. Copy the environment template:
```bash
cp .env.dist .env
```

2. Edit `.env` file with your credentials:
```bash
VOYAGE_API_KEY=your_voyageai_api_key_here
MONGODB_URI=mongodb://localhost:27017
```

3. Optionally, create a `config.json` file (see `config.json.example`):
```bash
cp config.json.example config.json
```

2. Add env variables and copy the real values

```bash
cp .env.dist .env
```

## Usage

### Test Connections

Test both VoyageAI and MongoDB connections:
```bash
uv run main.py test-connection
```

Test specific service:
```bash
# Test only VoyageAI
uv run main.py test-connection --service voyageai

# Test only MongoDB
uv run main.py test-connection --service mongodb
```

Verbose output:
```bash
uv run main.py test-connection --verbose
```

Override API key for testing:
```bash
uv run main.py test-connection --api-key your_test_api_key
```

### Initialize a New Project

Create a new project with default principles and guidelines:
```bash
# Basic project initialization
python main.py init my-project https://github.com/user/repo

# With project owners
python main.py init my-project https://github.com/user/repo --owner "alice@example.com" --owner "bob@example.com"

# Skip default seeding
python main.py init my-project https://github.com/user/repo --skip-defaults

# Verbose output
python main.py init my-project https://github.com/user/repo --verbose
```

### Process Text with VoyageAI

Generate embeddings for any text:
```bash
# Basic usage
uv run main.py prompt "Hello, world!"

# Different output formats
uv run main.py prompt "Your text here" --format summary
uv run main.py prompt "Your text here" --format full
uv run main.py prompt "Your text here" --format json
uv run main.py prompt "Your text here" --format embedding

# Specify model and input type
uv run main.py prompt "Your code here" --model voyage-code-2 --input-type document
uv run main.py prompt "search query" --input-type query

# Verbose output
uv run main.py prompt "Your text" --verbose
```

### Other Commands

```bash
# Say hello
uv run main.py hello "World"

# Say goodbye
uv run main.py goodbye "World"

# Get help
uv run main.py --help
```

## Features

- **VoyageAI Integration**: Connect to VoyageAI API for text embeddings
- **MongoDB Vector Search**: Store and search documents using vector embeddings
- **Configuration Management**: Flexible configuration via environment variables and JSON files
- **Connection Testing**: Comprehensive testing of service connections
- **Rich CLI Output**: Beautiful, informative command-line interface

## Project Structure

```
├── main.py                    # Main CLI entry point
├── src/
│   ├── voyageai_client.py    # VoyageAI API wrapper
│   ├── mongodb_client.py     # MongoDB connection and operations
│   ├── config.py            # Configuration management
│   └── commands/
│       └── test_connection.py # Connection testing command
├── config.json.example       # Sample configuration file
├── .env.dist                 # Environment variables template
└── pyproject.toml           # Project dependencies
```

## Dependencies

- `typer>=0.19.2` - CLI framework
- `voyageai>=0.2.0` - VoyageAI SDK
- `pymongo>=4.15.3` - MongoDB driver
- `python-dotenv>=1.0.0` - Environment variable loading
- `rich>=13.0.0` - Rich terminal output

## Development

To run the CLI in development mode:
```bash
python main.py test-connection --verbose
```

## Error Handling

The CLI provides comprehensive error handling and helpful messages for:
- Network connection issues
- Authentication failures
- Invalid configurations
- MongoDB connection problems
- Missing dependencies

## MongoDB Vector Search Setup

For vector search functionality, ensure your MongoDB instance supports vector search:
- MongoDB Atlas with vector search enabled, or
- Local MongoDB with appropriate vector index configuration

The tool will indicate whether vector indexes exist and provide guidance for setup.