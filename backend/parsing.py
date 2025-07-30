import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from typing import Dict, Any, List

# Configure Gemini API - get from environment variable
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
        print(f"Raw LLM response: {response.text}")

        # Clean the response text (NEW LOGIC)
        response_text = clean_llm_response(response.text)

        # Parse the JSON response
        result = json.loads(response_text)
        result = normalize_json_quotes(result)
        # Validate the structure as before     
        # Validate the structure
        if not isinstance(result, dict):
            raise Exception("Invalid JSON structure returned from LLM")
            
        return {
            "success": True,
            "data": result,
            "error": None
        }
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return error with the raw response
        return {
            "success": False,
            "data": None,
            "error": f"Failed to parse LLM response as JSON: {str(e)}. Raw response: {response.text[:200]}..."
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Error processing PDF: {str(e)}"
        }

def extract_text_chunks_from_pdf(pdf_path: str, pages_per_chunk: int = 2) -> List[str]:
    """
    Extract text from PDF in chunks of specified number of pages.
    
    Args:
        pdf_path: Path to the PDF file
        pages_per_chunk: Number of pages per chunk
        
    Returns:
        List of text chunks
    """
    try:
        doc = fitz.open(pdf_path)
        chunks = []
        current_chunk = ""
        page_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            if page_text:
                current_chunk += page_text + "\n"
                page_count += 1
                
                # Create chunk when we reach the page limit or at the end
                if page_count >= pages_per_chunk or page_num == len(doc) - 1:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = ""
                    page_count = 0
        
        return chunks
    except Exception as e:
        raise Exception(f"Error extracting text chunks from PDF: {str(e)}")

def process_chunk_with_gemini(chunk_text: str, chunk_num: int, total_chunks: int) -> Dict[str, Any]:
    """
    Process a single text chunk with Gemini LLM.
    
    Args:
        chunk_text: Text content of the chunk
        chunk_num: Current chunk number (1-based)
        total_chunks: Total number of chunks
        
    Returns:
        Parsed JSON response
    """

    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY environment variable is not set")
    
    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Create chunk-specific prompt
    chunk_prompt = f"""
    You are an expert at parsing construction specifications formatted in MasterFormat.

    Your job is to extract the technical content from the following PDF text and output it as structured JSON using the schema and nesting pattern provided below. This schema is an example only—the pattern applies to any MasterFormat specification document.

    **IMPORTANT: This is chunk {chunk_num} of {total_chunks} from a longer document.**
    - Extract content from this chunk only
    - Do not try to complete sections that span multiple chunks
    - Focus on the content present in this specific chunk

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

    PDF Text (Chunk {chunk_num} of {total_chunks}):
    {chunk_text}
    """
    
    try:
        # Generate response from Gemini
        response = model.generate_content(chunk_prompt)
        
        # Clean the response text using the new robust cleaning function
        response_text = clean_llm_response(response.text)
        
        # Parse and normalize JSON
        result = json.loads(response_text)
        normalized_result = normalize_json_quotes(result)
        
        return normalized_result
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse LLM response as JSON: {str(e)}. Raw response: {response.text[:200]}...")
    except Exception as e:
        raise Exception(f"Error processing chunk {chunk_num}: {str(e)}")

def merge_json_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple JSON responses by combining partItems arrays.
    
    Args:
        responses: List of JSON responses from chunks
        
    Returns:
        Merged JSON response
    """
    if not responses:
        raise Exception("No responses to merge")
    
    # Use the first response as the base structure
    merged = responses[0].copy()
    
    # Merge partItems for each part
    for part_name in ["part1", "part2", "part3"]:
        if part_name in merged:
            merged_part_items = merged[part_name].get("partItems", [])
            
            # Add partItems from other responses
            for response in responses[1:]:
                if part_name in response and "partItems" in response[part_name]:
                    merged_part_items.extend(response[part_name]["partItems"])
            
            # Update the merged response
            merged[part_name]["partItems"] = merged_part_items
    
    return merged

def parse_pdf_to_json_chunked(pdf_path: str, pages_per_chunk: int = 2) -> Dict[str, Any]:
    """
    Parse a MasterFormat PDF in chunks and merge the results.
    
    Args:
        pdf_path: Path to the PDF file
        pages_per_chunk: Number of pages per chunk
        
    Returns:
        Merged structured JSON data
    """
    try:
        # Extract text chunks
        text_chunks = extract_text_chunks_from_pdf(pdf_path, pages_per_chunk)
        
        if not text_chunks:
            raise Exception("No text content extracted from PDF")
        
        # Process each chunk with Gemini
        responses = []
        for i, chunk_text in enumerate(text_chunks, 1):
            response = process_chunk_with_gemini(chunk_text, i, len(text_chunks))
            responses.append(response)
        
        # Merge all responses
        merged_result = merge_json_responses(responses)
        
        return {
            "success": True,
            "data": merged_result,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Error processing PDF: {str(e)}"
        } 