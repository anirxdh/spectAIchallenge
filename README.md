# Coding Challenge 2025

Welcome! This is a 48-hour take-home coding challenge for candidates applying to the Full-Stack Software Engineer position at Spect AI.

---

## 🧠 Background

At Spect AI, we work with very large PDFs containing unstructured data submitted by construction engineers and architects. We need to parse out those unstructured data and format them in a structured way for further processing. We also need to display the structured data to users on a webpage. 

This take-home coding challenge is designed to simulate that work on a smaller scale by parsing out a specification in [MasterFormat](https://en.wikipedia.org/wiki/MasterFormat). As you will see, the we provide almost no code. You are expected to set up everything from scratch and read documentations on librarys that you may have never used before.

## 📌 Your Task
### Part 1 - Backend
Set up an API service using [FastAPI](https://fastapi.tiangolo.com) and [Uvicorn](https://www.uvicorn.org). This service should only have a single endpoint which takes in a PDF file returns its parsed contents in JSON format. You have to parse out the content verbatim from the PDF, with no rephrasing, summaries or omissions. Though you should ignore headers, footers, text on cover pages and other miscellaneous metadata.

You are expected to use Gemini. An API key will be provided to you separately. **DO NOT** commit the API key.

You are given 4 PDFs in the documents folder to test your code, with one of the specification PDFs already parsed into JSON. You must follow the JSON schema exactly (same JSON property names, same JSON value types). 

Your code should be generalizable. We will evaluate your code on more specifications written in MasterFormat.

### Part 2 - Frontend
Set up a [Next.js](https://nextjs.org/docs) frontend that connects to your backend. Present a simple webpage that will accept a PDF file. Then your backend should be called to fetch the specification's JSON representation. Pretty print the JSON on the webpage. Pay no attention to the stying of the webpage.

---

## 🚀 Submission Instructions
1. Fork this repo or create your own GitHub repo with your solution.
2. Make sure your repo includes:
  - Dependency control files (pyproject.toml, package.json, etc.)
  - Instructions to start your backend and frontend services locally
  - Your JSON output for the other 3 specification PDFs
  - A short write-up (`WRITEUP.md`) with:
    - Your approach and assumptions
    - Limitations or things you'd improve with more time
3. Email us the GitHub repo link (or zipped folder if needed)

---

## 🧠 Notes

- You're encouraged to use any tools, libraries, or AI coding assistants like ChatGPT, Cursor, Windsurf. This is the future 😀
- Be prepared to explain your approach and code in a following interview.
- If you have any questions, feel free to reach out at sunny@getspect.ai.

Good luck! We're excited to see your work 🚀

---
