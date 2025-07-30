import os
import json
import google.generativeai as genai
import fitz  # PyMuPDF
import re
from typing import Dict, Any, List

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Utility Functions ---

def normalize_quotes(text):
    """Normalize different types of quotes to standard quotes"""
    if not isinstance(text, str):
        return text
    return text.replace("’", "'").replace("‘", "'") \
               .replace("“", '"').replace("”", '"')
def normalize_json_quotes(obj):
    """Recursively normalize quotes in JSON object"""
    if isinstance(obj, dict):
        return {k: normalize_json_quotes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_json_quotes(item) for item in obj]
    elif isinstance(obj, str):
        return normalize_quotes(obj)
    else:
        return obj

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
    
    # Additional cleaning for common LLM issues
    json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
    json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas in arrays
    
    return json_text.strip()

# --- Text Extraction ---

def extract_pages_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text for each page in the PDF as a list.
    """
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            page_text = page.get_text()
            if page_text:
                pages.append(page_text.strip())
        doc.close()
        return pages
    except Exception as e:
        raise Exception(f"Error extracting pages from PDF: {str(e)}")

# --- Chunking Logic ---

def make_chunks(pages: List[str], chunk_size: int = 5, overlap: int = 1) -> List[List[str]]:
    """
    Splits list of pages into overlapping chunks.
    """
    chunks = []
    n = len(pages)

    i = 0
    while i < n:
        chunk = pages[i : min(i + chunk_size, n)]
        chunks.append(chunk)
        if i + chunk_size >= n:
            break
        print("start of chunk", i)
        print("end of chunk", min(i + chunk_size, n))
        i += chunk_size - overlap
    return chunks

# --- LLM Prompt Construction ---

def build_prompt(chunk_text: str, chunk_num: int, total_chunks: int) -> str:
    """
    Builds the LLM prompt for a given chunk.
    """
    return f"""
You are an expert at parsing construction specifications formatted in MasterFormat.

This is chunk {chunk_num} of {total_chunks}. Only extract and output content present in this chunk. Do not anticipate or repeat content from other chunks.

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

PDF Text (Chunk {chunk_num} of {total_chunks}):
\"\"\"
{chunk_text}
\"\"\"
"""

# --- LLM Call + JSON Parsing for One Chunk ---

def parse_chunk_with_gemini(prompt: str) -> Dict[str, Any]:
    """
    Sends prompt to Gemini, cleans and parses response, handles errors.
    """
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY environment variable is not set")
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    try:
        response = model.generate_content(prompt)
        response_text = clean_llm_response(response.text)
        
        try:
            result = json.loads(response_text)
            result = normalize_json_quotes(result)
            return result
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in chunk: {str(e)}")
            print(f"Raw response: {response_text[:200]}...")
            # Return empty structure instead of failing
            return {
                "section": "",
                "name": "",
                "part1": {"partItems": []},
                "part2": {"partItems": []},
                "part3": {"partItems": []}
            }
    except Exception as e:
        print(f"Error processing chunk with Gemini: {str(e)}")
        # Return empty structure instead of failing
        return {
            "section": "",
            "name": "",
            "part1": {"partItems": []},
            "part2": {"partItems": []},
            "part3": {"partItems": []}
        }

# --- Merge and Deduplicate ---

def deduplicate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate items based on index and text.
    """
    seen = set()
    result = []
    for item in items:
        identifier = (item.get('index'), item.get('text'))
        if identifier not in seen:
            result.append(item)
            seen.add(identifier)
    return result

def merge_json_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges the partItems arrays and deduplicates across chunks.
    """
    if not chunks:
        return {
            "section": "",
            "name": "",
            "part1": {"partItems": []},
            "part2": {"partItems": []},
            "part3": {"partItems": []}
        }
    
    # Use first non-empty chunk as base
    merged = None
    for chunk in chunks:
        if chunk.get('section') or chunk.get('name'):
            merged = chunk.copy()
            break
    
    if merged is None:
        merged = chunks[0].copy()
    
    # Merge partItems for each part
    for part in ['part1', 'part2', 'part3']:
        all_items = []
        for chunk in chunks:
            if part in chunk and isinstance(chunk[part], dict):
                part_items = chunk[part].get('partItems', [])
                all_items.extend(part_items)
        
        # Ensure part exists in merged result
        if part not in merged:
            merged[part] = {"partItems": []}
        elif not isinstance(merged[part], dict):
            merged[part] = {"partItems": []}
            
        merged[part]['partItems'] = deduplicate_items(all_items)
    
    return merged

# --- Main Entry Point for FastAPI ---

def parse_pdf_to_json_chunked(pdf_path: str, chunk_size: int = 5, overlap: int = 1) -> Dict[str, Any]:
    """
    Main pipeline: extract pages, chunk, process each chunk, merge, return output.
    """
    try:
        print(f"Starting chunked PDF parsing with chunk_size={chunk_size}, overlap={overlap}")
        
        # 1. Extract pages from PDF
        pages = extract_pages_from_pdf(pdf_path)
        print(f"Extracted {len(pages)} pages from PDF")
        
        # 2. Make overlapping chunks
        chunks = make_chunks(pages, chunk_size, overlap)
        total_chunks = len(chunks)
        print(f"Created {total_chunks} chunks")
        
        # 3. Process each chunk
        results = []
        for idx, chunk_pages in enumerate(chunks):
            print(f"Processing chunk {idx+1}/{total_chunks}")
            chunk_text = "\n".join(chunk_pages)
            prompt = build_prompt(chunk_text, idx+1, total_chunks)
            chunk_json = parse_chunk_with_gemini(prompt)
            results.append(chunk_json)
        
        # 4. Merge and deduplicate outputs
        print("Merging chunks...")
        merged = merge_json_chunks(results)
        
        # 5. Return the final result
        return {
            "success": True,
            "data": merged,
            "error": None
        }
        
    except Exception as e:
        print(f"Error in chunked parsing: {str(e)}")
        return {
            "success": False,
            "data": None,
            "error": f"Error processing PDF: {str(e)}"
        }

# --- Backward Compatibility ---

def parse_pdf_to_json(pdf_path: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility - now uses chunked approach.
    """
    return parse_pdf_to_json_chunked(pdf_path)