# Resume Analyzer

A complete, production-ready Resume Analyzer application built with **Python 3.12+**, **FastAPI**, **Jinja2**, **pdfplumber**, and **Google Gemini API** (`google-genai` SDK).

![Resume Analyzer Header](static/images/favicon.svg)

---

## Key Features

1. **PDF Resume Processing**
   - Drag & Drop PDF upload with real-time file size & extension validation (Up to 10MB).
   - Fast, resilient text extraction using `pdfplumber`.
   - Friendly handling for corrupted, empty, or unreadable PDF files.

2. **Automated Resume Evaluation**
   - **ATS Compatibility Score**: Calculated from 0 to 100 with visual animated circular gauge.
   - **Profile Executive Summary**: Concise summary of candidate experience.
   - **Skills Categorization**: Automatically extracts Technical and Soft skills.
   - **Missing Skills Detection**: Identifies critical industry skills missing from candidate's profile.
   - **Strengths & Weaknesses**: Highlight competitive advantages and gaps needing metrics or details.
   - **Actionable Recommendations**: Step-by-step guidance to raise resume score.
   - **Grammar & Formatting Edits**: Specific phrasing and action verb corrections.
   - **Suitable Job Roles & Experience Level**: Target roles matching profile.
   - **1-3 Year Career Roadmap**: Sequential growth milestones.
   - **Interview Prep Tips**: Tailored interview strategies based on resume content.

3. **Modern Responsive Web UI**
   - Dark Mode / Light Mode toggle (persisted via `localStorage`).
   - Glassmorphic navigation and card design system built with Vanilla CSS.
   - Interactive loading animations with step-by-step progress feedback.
   - Toast notifications for real-time validation and status updates.
   - One-click **Copy Summary** and **Export / Print PDF Report**.

---

## Project Structure

```text
resume-analyzer/
│
├── app.py                   # Main FastAPI app entry point & route registration
├── config.py                # Centralized settings & environment variables manager
├── requirements.txt         # Project dependencies
├── README.md                # Detailed project documentation
├── .env.example             # Environment variables template
├── .gitignore               # Git exclusion rules
├── uploads/                 # Directory for temporary file uploads
│   └── .gitkeep
│
├── routers/
│   ├── __init__.py
│   └── analyze.py           # API endpoints for PDF analysis and health checks
│
├── services/
│   ├── __init__.py
│   ├── gemini_service.py    # GenAI integration & JSON schema validation
│   └── pdf_service.py       # PDF validation and text extraction via pdfplumber
│
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Logging setup, text cleaning & custom exception handlers
│
├── templates/
│   └── index.html           # Main Jinja2 single-page application template
│
└── static/
    ├── css/
    │   └── style.css        # Premium responsive stylesheet (Dark/Light mode)
    ├── js/
    │   └── main.js          # File upload, async API fetch, DOM manipulation & toasts
    └── images/
        └── favicon.svg      # SVG icon branding
```

---

## Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- A **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

### 2. Environment Setup
Clone or navigate into the project root directory:

```bash
cd "d:/AI Resume"
```

Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
# Activate on Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Activate on Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
HOST=127.0.0.1
PORT=8000
MAX_UPLOAD_SIZE_MB=10
```

### 5. Run the Application
Launch the Uvicorn development server:

```bash
python app.py
```
*Or directly via Uvicorn:*
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the main web app UI |
| `GET` | `/api/health` | Service health check |
| `POST` | `/api/analyze` | Accepts multipart form upload of PDF resume file and returns structured analysis JSON |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## Security & Exception Handling
- **File Validation**: Strict enforcement of file extensions (`.pdf`), MIME types (`application/pdf`), and maximum file size (`10MB`).
- **Resilient Data Extraction**: Uses Pydantic structured output contracts (`response_schema`) with fallback regex cleanup for resilient JSON decoding.
- **Custom Exception Handlers**: Clear API error codes (400, 413, 422, 502) preventing raw tracebacks from exposing internal details to end users.
