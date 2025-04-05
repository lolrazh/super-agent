# Super Agent

An open-source Manus/Genspark clone for autonomous AI agents.

## Project Structure

```
app/
├── api/                   # API endpoints
│   ├── __init__.py
│   └── router.py         # Main API router
├── models/               # SQLAlchemy models
│   └── __init__.py
├── schemas/              # Pydantic schemas
│   └── __init__.py
├── agents/              # Agent implementation
│   └── __init__.py
├── tools/               # Tool implementation
│   └── __init__.py
├── services/            # Business logic
│   └── __init__.py
├── utils/               # Utility functions
│   └── __init__.py
├── config.py           # Application configuration
├── main.py             # FastAPI application
└── requirements.txt    # Python dependencies
```

## Setup Instructions

1. Create and activate a Python virtual environment:
```bash
# Using uv (recommended)
uv venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/macOS
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all modules, classes, and functions
- Keep functions small and focused
- Write tests for new functionality

## License

MIT 