import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from typing import Dict, Any, List

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

import fitz  # PyMuPDF

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
    return text.replace("’", "'").replace("‘", "'") \
               .replace("“", '"').replace("”", '"')
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

def fix_common_json_issues(json_text):
    """Fix common JSON issues that LLMs produce"""
    if not json_text:
        return json_text
    
    # Remove trailing commas before closing braces/brackets
    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
    
    # Only fix property names that are NOT already quoted
    # This regex looks for property names that don't start with a quote
    json_text = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):(?=\s*["{\[])', r'\1"\2"\3:', json_text)
    
    return json_text

def clean_llm_response(text):
    """Clean and extract JSON from LLM response"""
    if not text:
        return ""
    
    # Remove all code block markers
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    
    # Find the first opening brace
    start_idx = text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found in response")
    
    # Find the matching closing brace
    brace_count = 0
    end_idx = -1
    
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if end_idx == -1:
        raise ValueError("Unmatched braces in JSON response")
    
    # Extract the JSON part
    json_text = text[start_idx:end_idx]
    
    print(f"Extracted JSON length: {len(json_text)}")
    print(f"Extracted JSON preview: {json_text[:200]}...")
    
    # Additional cleaning for common LLM issues
    json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
    json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas in arrays
    
    return json_text.strip()
def parse_pdf_to_json(pdf_path: str) -> Dict[str, Any]:
    """
    Parse a MasterFormat PDF and convert it to structured JSON using Gemini LLM.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Structured JSON data
    """

    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY environment variable is not set")
    
    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)

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

    **Brief Sample Output:**
    (Note: Section names, indices, and content will change for each document. This is just an example.)

    {{
    "section": "238243",
    "name": "ELECTRIC HEATERS",
    "part1": {{
        "partItems": [
        {{
            "index": "1.01",
            "text": "SUMMARY",
            "children": [
            {{
                "index": "A.",
                "text": "Section includes requirements for electric heaters...",
                "children": null
            }},
            {{
                "index": "B.",
                "text": "This section includes requirements for LEED Certification...",
                "children": null
            }}
            ]
        }},
        {{
            "index": "1.02",
            "text": "REFERENCES",
            "children": [
            {{
                "index": "A.",
                "text": "This Section incorporates by reference the latest revisions of the following documents.",
                "children": [
                {{
                    "index": "1.",
                    "text": "National Fire Protection Agency (NFPA)",
                    "children": [
                    {{
                        "index": "a.",
                        "text": "NFPA 70 National Electrical Code",
                        "children": null
                    }}
                    ]
                }}
                ]
            }}
            ]
        }}
        ]
    }},
    "part2": {{
        "partItems": [
        {{
            "index": "2.01",
            "text": "ACCEPTABLE MANUFACTURERS:",
            "children": [
            {{
                "index": "A.",
                "text": "Berko Electric Heating; a division of Marley Engineered Products",
                "children": null
            }}
            ]
        }}
        ]
    }},
    "part3": {{
        "partItems": [
        {{
            "index": "3.01",
            "text": "INSTALLATION",
            "children": [
            {{
                "index": "A.",
                "text": "Install in conformance with the approved heater installation drawing, NFPA 70, UL listing, and manufacturer's instructions.",
                "children": null
            }}
            ]
        }}
        ]
    }}
    }}

    **Instructions for Output:**
    - Only return the JSON object matching the schema pattern above. Do **NOT** include any extra commentary, explanation, or markdown formatting.
    - For all "children", if there are no further sub-items, set the field to `null`.
    - If a section, part, or child does not exist in the document, output an empty array or `null` as appropriate.
    - Remove all unnecessary line breaks (`\\n`) that do not indicate a new list item, bullet, or paragraph.
    - Do **not** introduce extra spaces after periods or between words. Use a single space after each period.
    - Preserve paragraph separation only where a real new item/section begins (such as bullets, numbered lists, or headings).
    - Output all text fields as continuous, clean sentences, not split with `\\n` unless a new item/bullet is starting.

    PDF Text:
    {pdf_text}
    """
    
    try:
        # Generate response from Gemini
        response = model.generate_content(prompt)

        # Debug: Print the raw response
        print(f"Raw LLM response length: {len(response.text)}")
        print(f"Raw LLM response preview: {response.text[:500]}...")

        # Clean the response text
        try:
            response_text = clean_llm_response(response.text)
            print(f"Cleaned response length: {len(response_text)}")
            print(f"Cleaned response preview: {response_text[:500]}...")
        except ValueError as e:
            return {
                "success": False,
                "data": None,
                "error": f"Failed to clean LLM response: {str(e)}. Raw response: {response.text[:200]}..."
            }

        # Parse the JSON response
        try:
            # Try parsing the cleaned response directly first
            print(f"Attempting to parse cleaned response: {response_text[:200]}...")
            result = json.loads(response_text)
            result = normalize_json_quotes(result)
        except json.JSONDecodeError as e:
            print(f"First JSON parse attempt failed: {str(e)}")
            # If that fails, try with the fix function
            try:
                fixed_response = fix_common_json_issues(response_text)
                print(f"Attempting to parse fixed response: {fixed_response[:200]}...")
                result = json.loads(fixed_response)
                result = normalize_json_quotes(result)
            except json.JSONDecodeError as e2:
                # If JSON parsing fails, return error with the cleaned response
                print(f"JSON Parse Error: {str(e2)}")
                print(f"Error at line {e2.lineno}, column {e2.colno}")
                print(f"Error message: {e2.msg}")
                
                # Show the problematic area
                lines = response_text.split('\n')
                if e2.lineno <= len(lines):
                    print(f"Line {e2.lineno}: {lines[e2.lineno-1]}")
                    if e2.lineno > 1:
                        print(f"Line {e2.lineno-1}: {lines[e2.lineno-2]}")
                    if e2.lineno < len(lines):
                        print(f"Line {e2.lineno+1}: {lines[e2.lineno]}")
                
                return {
                    "success": False,
                    "data": None,
                    "error": f"Failed to parse LLM response as JSON: {str(e2)}. Raw response: {response_text[:500]}..."
                }
        
        # Validate the structure
        if not isinstance(result, dict):
            raise Exception("Invalid JSON structure returned from LLM")
            
        return {
            "success": True,
            "data": result,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Error processing PDF: {str(e)}"
        }
