# 📄 Resume Analyzer

An AI-powered Resume Analyzer built using **Python, FastAPI, Jinja2, pdfplumber, and Google Gemini API**. It analyzes PDF resumes and provides ATS scores, skills analysis, career guidance, and personalized improvement suggestions.

---

## 📸 Project Preview

<img width="1832" height="916" alt="Screenshot 2026-09-12 104126" src="https://github.com/user-attachments/assets/324ad6cd-8ae8-4b79-a3fd-ebb67431412c" />


---

## 🚀 Features

* 📄 PDF Resume Upload
* 🎯 ATS Compatibility Score (0–100)
* 👤 AI-Generated Profile Summary
* 🛠️ Technical & Soft Skills Extraction
* 🔍 Missing Skills Detection
* 💪 Strengths & Weaknesses Analysis
* 💡 Resume Improvement Suggestions
* ✍️ Grammar & Formatting Suggestions
* 💼 Suitable Job Roles
* 📈 Experience Level Analysis
* 🗺️ 1–3 Year Career Roadmap
* 🎤 Interview Preparation Tips
* 🌙 Dark / Light Mode
* 📋 Copy Summary
* 📄 Export / Print Report

---

## 🛠️ Tech Stack

### Backend

* Python 3.12+
* FastAPI
* Jinja2
* Uvicorn

### AI & Processing

* Google Gemini API
* Google GenAI SDK
* pdfplumber

### Frontend

* HTML
* CSS
* JavaScript
* Vanilla CSS

---

## 🏗️ Project Structure

```text
resume-analyzer/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── uploads/
│   └── .gitkeep
│
├── routers/
│   ├── __init__.py
│   └── analyze.py
│
├── services/
│   ├── __init__.py
│   ├── gemini_service.py
│   └── pdf_service.py
│
├── utils/
│   ├── __init__.py
│   └── helpers.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── images/
        ├── favicon.svg
        ├── home.png
        ├── upload.png
        └── result.png
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/Resume-Analyzer.git
cd Resume-Analyzer
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
HOST=127.0.0.1
PORT=8000
MAX_UPLOAD_SIZE_MB=10
```

⚠️ **Never upload your `.env` file or API key to GitHub.**

---

## ▶️ Run the Application

```bash
python app.py
```

Or:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open in browser:

```text
http://127.0.0.1:8000
```

---

## 🔄 How It Works

```text
PDF Resume Upload
        ↓
PDF Validation
        ↓
Text Extraction
        ↓
Google Gemini AI
        ↓
Resume Analysis
        ↓
ATS Score + Skills + Suggestions
        ↓
Career & Interview Guidance
```

---

## 🔗 API Endpoints

| Method | Endpoint       | Description               |
| ------ | -------------- | ------------------------- |
| GET    | `/`            | Main application          |
| GET    | `/api/health`  | Health check              |
| POST   | `/api/analyze` | Analyze PDF resume        |
| GET    | `/docs`        | Swagger API documentation |

---

## 🎯 Use Cases

* Students preparing for placements
* Job seekers
* Resume improvement
* ATS optimization
* Skill gap analysis
* Career planning
* Interview preparation

---

## 🔮 Future Scope

* Job Description matching
* Resume-to-job matching
* ATS score comparison
* AI-powered resume rewriting
* Job recommendation system
* LinkedIn profile analysis
* Advanced analytics dashboard

---
