# MasterFormat PDF Parser - Backend

FastAPI backend service for parsing MasterFormat PDF specifications into structured JSON format using Google's Gemini LLM.

## Features

- 🚀 FastAPI with automatic API documentation
- 📄 PDF text extraction using PyPDF2
- 🤖 AI-powered parsing using Google Gemini LLM
- 🔒 CORS configured for frontend (localhost:3000)
- 📊 Structured JSON output
- 🧪 Health check endpoint

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.8+
- **PDF Processing**: PyPDF2
- **AI/LLM**: Google Gemini
- **Server**: Uvicorn

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Install dependencies:**
```bash
pip install fastapi uvicorn python-multipart google-generativeai PyPDF2 pydantic
```

2. **Set up environment variables:**
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

3. **Start the server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### POST `/parse`
Parse a MasterFormat PDF file and return structured JSON.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file in the `file` field

**Response:**
```json
{
  "success": true,
  "data": {
    "specification_number": "23 82 43",
    "title": "Electric Heaters",
    "sections": [
      {
        "section_number": "1.1",
        "title": "Summary",
        "content": "..."
      }
    ],
    "submittals": [...],
    "quality_assurance": [...]
  },
  "error": null
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "MasterFormat PDF Parser API is running"
}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── parsing.py           # PDF parsing logic
├── pyproject.toml       # Dependencies
└── README.md           # This file
```

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

## Error Handling

The API handles various error scenarios:
- Invalid file types (non-PDF)
- Missing API keys
- PDF parsing errors
- LLM processing errors
- JSON parsing errors

All errors return appropriate HTTP status codes and error messages. 