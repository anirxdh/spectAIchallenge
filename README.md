# MasterFormat PDF Parser - Coding Challenge 2025

A full-stack application that parses MasterFormat PDF specifications into structured JSON format using AI-powered processing. Built with FastAPI backend and Next.js frontend.

## 🚀 Features

- **PDF Processing**: Extracts text and tables from MasterFormat PDFs
- **AI-Powered Parsing**: Uses Google Gemini LLM for intelligent content structuring
- **Chunked Processing**: Handles large PDFs with overlapping chunk strategy
- **Modern UI**: Dark theme with mobile-responsive design
- **Real-time Feedback**: Enhanced loading experience with progress indicators
- **Error Handling**: Comprehensive error management and user feedback

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI with Uvicorn
- **Language**: Python 3.8+
- **PDF Processing**: fitz (PyMuPDF) + pdfplumber
- **AI/LLM**: Google Gemini
- **Dependencies**: See `backend/pyproject.toml`

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom dark theme
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Dependencies**: See `frontend/package.json`

## 📁 Project Structure

```
coding-challenge-2025/
├── backend/                    # FastAPI backend service
│   ├── main.py                # FastAPI application
│   ├── parsing.py             # PDF parsing logic
│   ├── pyproject.toml         # Python dependencies (modern)
│   ├── requirements.txt        # Python dependencies (traditional)
│   └── README.md              # Backend setup instructions
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   └── components/        # React components
│   ├── package.json           # Node.js dependencies
│   └── README.md              # Frontend setup instructions
├── documents/                  # Test PDF files
├── json_outputs/              # Parsed JSON outputs
│   ├── README.md              # JSON outputs documentation
│   └── *.json                 # Parsed specification files
├── WRITEUP.md                 # Approach and limitations
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** and **Node.js 18+**
- **Google Gemini API Key** (provided separately)
- **Git** for cloning the repository

### 1. Clone and Setup

```bash
git clone https://github.com/anirxdh/spectAIchallenge.git
cd spectAIchallenge
```

### 2. Backend Setup

```bash
cd backend

# Option 1: Install using pyproject.toml (recommended)
pip install -e .

# Option 2: Install using requirements.txt (alternative)
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key_here"

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Usage

1. Open `http://localhost:3000` in your browser
2. Drag and drop a MasterFormat PDF file or click to browse
3. Click "Parse PDF" to process the document
4. View the structured JSON output with syntax highlighting

## 📊 API Endpoints

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
    "section": "23 82 43",
    "name": "Electric Heaters",
    "part1": {
      "partItems": [...]
    },
    "part2": {
      "partItems": [...]
    },
    "part3": {
      "partItems": [...]
    }
  },
  "error": null
}
```

### GET `/health`
Health check endpoint.

## 📄 JSON Outputs

The `json_outputs/` folder contains parsed JSON files for all test specifications:

- ✅ `22_08_00_commissioning_plumbing_short.json` - Commissioning of Plumbing (Short)
- ✅ `23_82_43_electric_heaters.json` - Electric Heaters
- ✅ `271500_medium.json` - Horizontal Cabling Requirements
- ⏳ `233000_hvac_air_distribution_long.json` - HVAC Air Distribution (Long)

## 🔧 Development

### Backend Development
```bash
cd backend
# Run with auto-reload
uvicorn main:app --reload

# API Documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Frontend Development
```bash
cd frontend
# Development server
npm run dev

# Build for production
npm run build
npm start

# Linting
npm run lint
```

## 📋 Dependencies

### Backend Dependencies
**Primary**: `backend/pyproject.toml` (modern approach)
**Alternative**: `backend/requirements.txt` (traditional approach)

**Core Dependencies:**
- fastapi - Web framework
- uvicorn - ASGI server
- python-multipart - File upload handling
- google-generativeai - Gemini LLM integration
- PyPDF2 - PDF processing
- pydantic - Data validation
- python-dotenv - Environment variables
- PyMuPDF (fitz) - PDF text extraction
- pdfplumber - PDF table extraction
- typing-extensions - Type hints support

### Frontend Dependencies (`frontend/package.json`)
- next.js
- react
- typescript
- tailwindcss
- framer-motion
- lucide-react
- react-syntax-highlighter

## 🎯 Approach

See `WRITEUP.md` for detailed information about:
- Development approach and iterations
- Technical challenges and solutions
- Known limitations
- Future improvements

## 📝 License

This project was created for the Spect AI coding challenge 2025.

---

**Contact**: For questions about this implementation, please refer to the `WRITEUP.md` file for technical details and approach explanation.
