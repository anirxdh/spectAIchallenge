import os
import json
import google.generativeai as genai
import fitz  # PyMuPDF
import re
import pdfplumber
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

def extract_pages_and_tables(pdf_path: str):
    # Extract page text with fitz
    doc = fitz.open(pdf_path)
    pages = [page.get_text().strip() for page in doc]
    doc.close()
    
    # Extract tables with pdfplumber
    tables_per_page = extract_tables_by_page(pdf_path)
    
    # Combine: returns a list of dicts per page
    result = []
    for idx, page_text in enumerate(pages):
        entry = {
            "text": page_text,
            "tables": tables_per_page[idx] if idx < len(tables_per_page) else []
        }
        result.append(entry)
    return result

def extract_tables_by_page(pdf_path: str) -> List[List[dict]]:
    """
    Extract tables for each page as a list (indexed by page number).
    """
    tables_per_page = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = []
            for tbl in page.extract_tables():
                if not tbl or not tbl[0]:
                    continue
                headers = tbl[0]
                rows = tbl[1:]
                tables.append({
                    "headers": headers,
                    "rows": rows
                })
            tables_per_page.append(tables)
    return tables_per_page

# --- Chunking Logic ---

def make_chunks(pages: List[dict], chunk_size: int = 5, overlap: int = 1) -> List[List[dict]]:
    """
    Splits list of page dicts (each with 'text' and 'tables') into overlapping chunks.
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

def build_prompt(chunk_pages: List[dict], chunk_num: int, total_chunks: int) -> str:
    """
    Builds the LLM prompt for a given chunk.
    """
    # Join all text and tables in this chunk
    text_blocks = []
    for page in chunk_pages:
        text_blocks.append(page['text'])
        # Add tables as markdown, so Gemini can "see" them in the chunk
        for tbl in page.get('tables', []):
            headers = " | ".join(str(h) for h in tbl['headers'])
            separator = " | ".join(['---'] * len(tbl['headers']))
            rows = "\n".join(" | ".join(str(cell) for cell in row) for row in tbl['rows'])
            table_md = f"\nTABLE:\n| {headers} |\n| {separator} |\n{rows}\n"
            text_blocks.append(table_md)
    chunk_text = "\n".join(text_blocks)
    
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

    - If there are any tables present, add them as a "tables" field (see schema below). Use the headers and rows as shown. Do not omit or summarize tables.
    - If a table is related to a heading or subsection (e.g., "2.1 HORIZONTAL CABLE"), place the tables array inside the same object as "index": "2.1".
	- Do not attach all tables at the root. Only attach a table to the nearest relevant section/subsection. Use the following format for each table:

    **Table Example:**

    {{
    "index": "2.1",
    "text": "HORIZONTAL CABLE",
    "tables": [
        {{
        "title": "Test Parameter Table 1",
        "headers": ["Test Parameter", "100 MHz", "250 MHz"],
        "rows": [
            ["Attenuation:", "22.0 dB", "36.9 dB"],
            ["NEXT:", "35.3 dB", "31.3 dB"]
        ]
        }}
    ]
    }}

    **Instructions for Output:**
    - Only return the JSON object matching the schema pattern above. Do **NOT** include any extra commentary, explanation, or markdown formatting.
    - For all "children", if there are no further sub-items, set the field to `null`.
    - If a section, part, or child does not exist in the document, output an empty array or `null` as appropriate.
    - Remove all unnecessary line breaks (`\\n`) that do not indicate a new list item, bullet, or paragraph.
    - Do **not** introduce extra spaces after periods or between words. Use a single space after each period.
    - Preserve paragraph separation only where a real new item/section begins (such as bullets, numbered lists, or headings).
    - Output all text fields as continuous, clean sentences, not split with `\\n` unless a new item/bullet is starting.
    - When a major bullet or section (like '7.' or '8.') is immediately followed by sub-bullets (like 'a.', 'b.'), output the main bullet as an object with a 'children' array, each sub-bullet as its own child. Never flatten sub-bullets into the parent text. Show this with an explicit example in the prompt.
    - “If a section header appears near the start or end of the chunk and seems incomplete, extract it with whatever content is available; do not skip it.”

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

def table_hash(tbl):
    """Create a hash for table deduplication"""
    # Use headers + all rows for hashable tuple
    return (tuple(tbl['headers']), tuple(tuple(row) for row in tbl['rows']))

def dedupe_tables(node, seen_tables=None):
    """Recursively deduplicate tables in the JSON structure"""
    if seen_tables is None:
        seen_tables = set()
    # Dedupe tables at this node
    if 'tables' in node:
        unique_tables = []
        for tbl in node['tables']:
            thash = table_hash(tbl)
            if thash not in seen_tables:
                unique_tables.append(tbl)
                seen_tables.add(thash)
        node['tables'] = unique_tables
    # Recurse to children
    for k in ['children', 'partItems']:
        if k in node and node[k]:
            for child in node[k]:
                dedupe_tables(child, seen_tables)

def remove_empty_tables(node):
    """Remove empty 'tables' fields at any level"""
    if isinstance(node, dict):
        # Remove tables if empty
        if 'tables' in node and isinstance(node['tables'], list) and not node['tables']:
            del node['tables']
        # Recurse for all keys
        for k, v in node.items():
            remove_empty_tables(v)
    elif isinstance(node, list):
        for item in node:
            remove_empty_tables(item)
def tables_to_markdown(node):
    """
    Recursively traverse the JSON structure.
    If a node contains 'tables', append their markdown to the 'text' field,
    and remove the 'tables' key.
    """
    if isinstance(node, dict):
        # Process tables at this node
        if 'tables' in node and isinstance(node['tables'], list) and node['tables']:
            md_tables = []
            for tbl in node['tables']:
                headers = " | ".join(str(h) for h in tbl['headers'])
                separator = " | ".join(['---'] * len(tbl['headers']))
                rows = "\n".join(" | ".join(str(cell) for cell in row) for row in tbl['rows'])
                title = f"**{tbl.get('title', '')}**\n" if tbl.get('title') else ""
                table_md = f"{title}| {headers} |\n| {separator} |\n{rows}"
                md_tables.append(table_md)
            # Append the markdown tables to the text field
            if 'text' in node and isinstance(node['text'], str):
                node['text'] = node['text'].rstrip() + "\n\n" + "\n\n".join(md_tables)
            else:
                node['text'] = "\n\n".join(md_tables)
            # Remove the original 'tables' array
            del node['tables']
        # Recursively process children/partItems
        for k in ['children', 'partItems']:
            if k in node and node[k]:
                for child in node[k]:
                    tables_to_markdown(child)
    elif isinstance(node, list):
        for item in node:
            tables_to_markdown(item)
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
    def merge_part_items(all_items):
        seen = {}
        for item in all_items:
            idx = item.get('index')
            # Prefer item with more children, then longer text
            if idx in seen:
                prev = seen[idx]
                prev_children = prev.get('children') or []
                curr_children = item.get('children') or []
                if len(str(curr_children)) > len(str(prev_children)):
                    seen[idx] = item
                elif len(str(curr_children)) == len(str(prev_children)):
                    # Fall back to longer text
                    if len(str(item.get('text', ''))) > len(str(prev.get('text', ''))):
                        seen[idx] = item
            else:
                seen[idx] = item
        return list(seen.values())
    
    # Merge as before, but use new merge_part_items
    merged = None
    for chunk in chunks:
        if chunk.get('section') or chunk.get('name'):
            merged = chunk.copy()
            break
    if merged is None:
        merged = chunks[0].copy()
    for part in ['part1', 'part2', 'part3']:
        all_items = []
        for chunk in chunks:
            if part in chunk and isinstance(chunk[part], dict):
                part_items = chunk[part].get('partItems', [])
                all_items.extend(part_items)
        merged[part]['partItems'] = merge_part_items(all_items)
    return merged

# --- Main Entry Point for FastAPI ---

def parse_pdf_to_json_chunked(pdf_path: str, chunk_size: int = 5, overlap: int = 1) -> Dict[str, Any]:
    """
    Main pipeline: extract pages, chunk, process each chunk, merge, return output.
    """
    try:
        print(f"Starting chunked PDF parsing with chunk_size={chunk_size}, overlap={overlap}")
        
        # 1. Extract pages from PDF
        pages = extract_pages_and_tables(pdf_path)
        print(f"Extracted {len(pages)} pages from PDF")
        
        # 2. Make overlapping chunks
        chunks = make_chunks(pages, chunk_size, overlap)
        total_chunks = len(chunks)
        print(f"Created {total_chunks} chunks")
        
        # 3. Process each chunk
        results = []
        for idx, chunk_pages in enumerate(chunks):
            print(f"Processing chunk {idx+1}/{total_chunks}")
            prompt = build_prompt(chunk_pages, idx+1, total_chunks)
            chunk_json = parse_chunk_with_gemini(prompt)
            results.append(chunk_json)
        
        # 4. Merge and deduplicate outputs
        print("Merging chunks...")
        merged = merge_json_chunks(results)
        
        # 5. Deduplicate tables across the entire structure
        print("Deduplicating tables...")
        dedupe_tables(merged)
        
        # 6. Convert tables to markdown and inline in text fields
        print("Converting tables to markdown and inlining...")
        tables_to_markdown(merged)
        
        # 7. Remove any empty tables arrays (for safety)
        remove_empty_tables(merged)
        
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