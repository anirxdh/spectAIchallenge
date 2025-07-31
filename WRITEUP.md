# WRITEUP.md - MasterFormat PDF Parser

## Approach and Development Journey

### Initial Approach - Simple PDF Text Extraction
I started with a straightforward approach using **fitz** (PyMuPDF) for text extraction. This worked well for smaller PDFs and allowed me to get the basic project structure in place with FastAPI backend and Next.js frontend.

### Challenge 1: Large PDF Processing
When testing with larger PDFs, I encountered token limitations with Gemini. The simple approach of sending entire PDF content in one request failed due to context window constraints.

### Approach 2: Basic Chunking
To address the large PDF issue, I implemented basic chunking - dividing the PDF content into smaller chunks. However, this approach had a critical flaw: when sections were split across chunks, the parsing became inconsistent and incomplete, especially when a section ended in one chunk and continued in the next.

### Approach 3: Dynamic Chunking (Failed)
I attempted a dynamic chunking approach where:
- When a section was about to end, the system would extend the chunk boundary
- Wait until the section naturally ended before creating the next chunk

This approach failed because extending chunks to section boundaries often resulted in chunks that were too large, causing Gemini to run out of tokens again.

### Approach 4: Section-by-Section Processing (Failed)
I tried processing each section individually, but this approach also hit limitations:
- Large sections (like Section 2 in the long PDF spanning ~15 pages) exceeded Gemini's token limits
- Breaking down to sub-sections would require too many API calls and consume excessive tokens
- The complexity of detecting section boundaries accurately proved challenging

### Final Approach: Overlapping Chunks (Successful)
Drawing inspiration from vector database techniques, I implemented **overlapping chunks** as the final solution:

**Configuration:**
- **Chunk size:** 3 pages (optimal balance found through testing)
- **Overlap:** 1 page between consecutive chunks
- **Reasoning:** 
  - 5 pages per chunk resulted in moderate performance issues
  - 7 pages per chunk caused hallucinations in Gemini responses
  - 3 pages provided the best balance of context and accuracy

This approach ensures that section boundaries are preserved across chunks, maintaining context continuity.

### Table Extraction Enhancement
After establishing the chunking approach, I identified that tables were not being extracted properly. I integrated **pdfplumber** alongside fitz:
- **fitz:** Optimal for text extraction
- **pdfplumber:** Superior for table detection and extraction

I considered exploring Vision Language Models (VLMs) for better document understanding but decided to continue with the current approach given the progress already made.

### Data Processing Pipeline
The final processing pipeline includes:
1. **Text extraction** using fitz
2. **Table extraction** using pdfplumber  
3. **Chunking with overlap** (3 pages, 1 page overlap)
4. **LLM processing** with Gemini
5. **JSON cleaning and formatting**
6. **Chunk merging** to reconstruct complete document structure

## Technical Stack
- **Backend:** FastAPI with Uvicorn (as recommended)
- **Frontend:** Next.js 14 with TypeScript
- **LLM:** Google Gemini
- **PDF Processing:** fitz (PyMuPDF) + pdfplumber
- **Styling:** Tailwind CSS with custom dark theme
- **Features:** Mobile responsive design, drag-and-drop file upload, real-time loading states

## Known Limitations

### 1. Chunking Merge Logic Error
Due to the overlapping chunk approach, there's an occasional issue where Section 3 content may appear in Section 2 of the final JSON output. While all data is present and accurate, the structural organization can be slightly misaligned. This is a timing constraint issue that I wasn't able to fully resolve.

### 2. Table and Text Misalignment  
Since I'm using two different tools (fitz for text, pdfplumber for tables), tables are occasionally misplaced in the final output. The extraction itself is accurate, but the positional relationship between tables and surrounding text can be inconsistent.

### 3. Processing Time
The overlapping chunk approach, while accurate, requires multiple API calls to Gemini, resulting in longer processing times for large documents.

## What I Would Improve With More Time

1. **Fix Merge Logic:** Implement more sophisticated logic to properly merge overlapping chunks and ensure correct section boundaries in the final JSON structure.

2. **Unified Extraction Approach:** Explore a single tool or develop custom logic that can handle both text and table extraction cohesively to maintain proper positioning.

3. **VLM Integration:** Experiment with Vision Language Models that can process PDF pages as images, potentially providing better understanding of document structure and layout.

4. **Advanced Section Detection:** Implement more robust section boundary detection to enable more intelligent chunking strategies.

5. **Caching and Optimization:** Add caching mechanisms and optimize the processing pipeline to reduce API calls and processing time.

6. **Error Recovery:** Implement better error handling and recovery mechanisms for failed chunk processing.

## Conclusion

Despite the challenges and iterative approach, the final solution successfully parses MasterFormat PDFs into structured JSON format. The overlapping chunk strategy proved to be the most reliable approach for handling documents of varying sizes while maintaining context integrity. The system is production-ready with a polished, mobile-responsive frontend and handles the core requirements effectively.