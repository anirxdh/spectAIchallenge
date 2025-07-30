# MasterFormat PDF to JSON Parser - Frontend

A modern Next.js 14 application with a dark theme UI for parsing MasterFormat PDF specifications into structured JSON format.

## Features

- 🎨 Modern dark theme UI with Tailwind CSS
- 📁 Drag and drop file upload with validation
- ⚡ Real-time loading states and error handling
- 📄 Syntax-highlighted JSON output
- 📱 Responsive design for mobile and desktop
- 🔒 File type and size validation (PDF only, max 10MB)

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom dark theme
- **Icons**: Lucide React
- **Syntax Highlighting**: React Syntax Highlighter

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Development

The app expects a backend API running at `http://localhost:8000` with a `/parse` endpoint that accepts multipart/form-data with a PDF file.

## Project Structure

```
src/
├── app/
│   ├── globals.css          # Global styles and dark theme
│   ├── layout.tsx           # Root layout with dark mode
│   └── page.tsx             # Main page component
└── components/
    ├── FileDropzone.tsx     # File upload component
    ├── LoadingSpinner.tsx   # Loading animation
    ├── JsonViewer.tsx       # JSON display with syntax highlighting
    └── ErrorAlert.tsx       # Error message component
```

## API Integration

The frontend sends POST requests to `http://localhost:8000/parse` with:
- Content-Type: `multipart/form-data`
- Body: PDF file in the `file` field

Expected response format:
```json
{
  "success": true,
  "data": { /* parsed JSON data */ },
  "error": null
}
```

## Build for Production

```bash
npm run build
npm start
```
