#!/usr/bin/env python3

import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from typing import Dict, Any, List
from dotenv import load_dotenv
import time
import fitz  # PyMuPDF

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def normalize_quotes(text):
    if not isinstance(text, str):
        return text
    return text.replace("'", "'").replace("'", "'") \
               .replace(""", '"').replace(""", '"')
               
def normalize_json_quotes(obj):
    if isinstance(obj, dict):
        return {k: normalize_json_quotes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_json_quotes(item) for item in obj]
    elif isinstance(obj, str):
        return normalize_quotes(obj)
    else:
        return obj

import re

def clean_llm_response(text):
    # Remove all code block markers
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    # Remove all text before the first curly brace
    text = re.sub(r'^[^\{]*({.*)', r'\1', text, flags=re.DOTALL)
    # Remove everything after the last closing curly brace
    match = re.search(r'(\{.*\})', text, flags=re.DOTALL)
    if match:
        text = match.group(1)
    return text.strip()

def parse_pdf_to_json_robust(pdf_path: str) -> Dict[str, Any]:
    """
    Robust PDF parser with better error handling and API key validation.
    """
    
    # Validate API key
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "data": None,
            "error": "GEMINI_API_KEY environment variable is not set"
        }
    
    print(f"🔑 Using API key: {GEMINI_API_KEY[:20]}...")
    
    # Test API key first
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try different model versions in order of preference
        model_versions = ['gemini-1.5-pro', 'gemini-1.5-pro-latest', 'gemini-pro']
        model = None
        
        for version in model_versions:
            try:
                print(f"🧪 Testing model: {version}")
                test_model = genai.GenerativeModel(version)
                test_response = test_model.generate_content("Test")
                model = test_model
                print(f"✅ Successfully using model: {version}")
                break
            except Exception as e:
                print(f"❌ Model {version} failed: {str(e)}")
                continue
        
        if not model:
            return {
                "success": False,
                "data": None,
                "error": "No working Gemini model found"
            }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"API key validation failed: {str(e)}"
        }
    
    # Extract text from PDF
    try:
        pdf_text = extract_text_from_pdf(pdf_path)
        print(f"📄 Extracted {len(pdf_text)} characters from PDF")
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"PDF extraction failed: {str(e)}"
        }

    prompt = f"""
    You are an expert at parsing construction specifications formatted in MasterFormat.

    Your job is to extract the technical content from the following PDF text and output it as structured JSON using the schema and nesting pattern provided below. This schema is an example only—the pattern applies to any MasterFormat specification document.

    **Critical Instructions:**
    - Extract all content **verbatim** from the PDF. Do **NOT** summarize, rephrase, or omit any technical content.
    - **Ignore** all headers, footers, cover page text, and miscellaneous metadata.
    - **Generalize:** The output should follow the schema pattern exactly, but section numbers, part names, indices, and headings may vary in each document. Handle any number or label as found in the text, and include any section, part, or subitem you find, regardless of names or order.
    - If a part or section is missing in the document, output it as an empty array or `null` as appropriate.
    - Only output valid JSON, with no explanations, markdown, or extra text.

    **Schema Example:**
    {{
    "section": "string",      // MasterFormat section number (e.g., "238243")
    "name": "string",         // Section name/title (e.g., "ELECTRIC HEATERS")
    "part1": {{
        "partItems": [
        {{
            "index": "string",    // Section/part index (e.g., "1.01")
            "text": "string",     // Title or description (e.g., "SUMMARY")
            "children": [
            {{
                "index": "string",
                "text": "string",
                "children": [
                {{
                    "index": "string",
                    "text": "string",
                    "children": null
                }}
                ]
            }},
            // ... (can be further nested, or null if none)
            ]
        }}
        ]
    }},
    "part2": {{
        "partItems": [
        // ... repeat same structure as part1
        ]
    }},
    "part3": {{
        "partItems": [
        // ... repeat same structure as part1
        ]
    }}
    }}

    PDF Text:
    {pdf_text[:4000]}...
    """
    
    try:
        # Generate response with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🚀 Attempt {attempt + 1} to generate content...")
                response = model.generate_content(prompt)
                
                # Clean the response text
                response_text = clean_llm_response(response.text)
                
                # Parse the JSON response
                result = json.loads(response_text)
                result = normalize_json_quotes(result)
                
                # Validate the structure
                if not isinstance(result, dict):
                    raise Exception("Invalid JSON structure returned from LLM")
                
                print("✅ Successfully parsed PDF!")
                return {
                    "success": True,
                    "data": result,
                    "error": None
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "data": None,
                        "error": f"Failed to parse LLM response as JSON after {max_retries} attempts: {str(e)}"
                    }
                time.sleep(2)  # Wait before retry
                
            except Exception as e:
                print(f"❌ Generation failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "data": None,
                        "error": f"Error generating content after {max_retries} attempts: {str(e)}"
                    }
                time.sleep(2)  # Wait before retry
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Unexpected error during processing: {str(e)}"
        } 