from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
import os
import tempfile
from parsing import parse_pdf_to_json  # You'll create this function in parsing.py

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✅ API key loaded from environment: {api_key[:20]}...")
else:
    print("❌ API key not found in environment variables")

app = FastAPI(
    title="MasterFormat PDF Parser",
    description="Backend API for parsing MasterFormat PDFs to structured JSON using Gemini LLM.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse_endpoint(file: UploadFile = File(...)) -> Any:
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Save uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Call your parsing function (LLM logic goes in parsing.py)
        result_json = parse_pdf_to_json(tmp_path)

        # Optionally validate the output here

        return result_json
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "MasterFormat PDF Parser API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 