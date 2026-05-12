# Career Advisor Backend

FastAPI backend service for the Career Advisor application. Handles business logic, orchestration, file uploads, and coordinates with AWS Strands ReACT agent for AI analysis.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Pydantic Validation**: Type-safe request/response validation
- **CORS Support**: Configured for frontend integration
- **Environment Configuration**: Flexible configuration via environment variables
- **Modular Architecture**: Clean separation of concerns with routers, services, and models

## Requirements

- Python 3.11 or higher
- pip (Python package manager)

## Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Project Structure

```
backend/
├── main.py                 # Application entry point
├── app/
│   ├── __init__.py
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   └── v1/           # API version 1
│   │       ├── __init__.py
│   │       └── endpoints/ # Endpoint modules
│   ├── core/             # Core configuration
│   │   ├── __init__.py
│   │   └── config.py     # Settings and environment variables
│   ├── models/           # Database models
│   │   └── __init__.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── __init__.py
│   │   └── common.py     # Common schemas
│   └── services/         # Business logic
│       └── __init__.py
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `ENVIRONMENT`: Environment (development, staging, production)
- `DEBUG`: Debug mode (True/False)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- `AWS_STRANDS_AGENT_ID`: AWS Strands ReACT agent ID
- `BRAVE_SEARCH_API_KEY`: Brave Search API key

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

### Linting

```bash
flake8 .
```

## Deployment

The backend can be deployed to:
- AWS Lambda (with Mangum adapter)
- Railway
- Any platform supporting Python ASGI applications

## License

Proprietary - Career Advisor Project
