# 🔬 AI Endoscopy Clinical Decision Support System

> **An Agentic AI platform for endoscopy image analysis powered by Swin Transformer, Grad-CAM, RAG, and Google Gemini — delivering automated clinical reports with evidence-based recommendations.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1.4-FF6B35)
![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Supported Conditions](#supported-conditions)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Agentic Pipeline](#agentic-pipeline)
- [RAG Knowledge Base](#rag-knowledge-base)
- [Docker Deployment](#docker-deployment)
- [Sample Images](#sample-images)
- [Contributing](#contributing)

---

## 🧠 Overview

This project is an **Agentic AI-powered Clinical Decision Support System (CDSS)** for gastrointestinal endoscopy. It combines state-of-the-art computer vision with large language models and retrieval-augmented generation to assist clinicians in:

- Automatically **classifying GI conditions** from endoscopy images
- Generating **Grad-CAM heatmaps** to visually highlight regions of interest
- Performing **AI-driven severity assessment** with lesion coverage quantification
- Retrieving **evidence-based treatment guidelines** via a RAG pipeline
- Producing **structured clinical PDF reports** with cited medical literature

The system is designed for clinical research and educational use, supporting endoscopists, gastroenterologists, and medical trainees.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖼️ **Image Classification** | Swin Transformer-based classification of 5 GI conditions |
| 🔥 **Grad-CAM Heatmaps** | Visual explanations highlighting lesion regions of interest |
| 📊 **Severity Assessment** | Automated lesion coverage % with Mild / Moderate / Severe grading |
| 🤖 **Agentic Orchestration** | LangGraph 6-node pipeline for end-to-end clinical reasoning |
| 📚 **RAG Pipeline** | FAISS-indexed knowledge base with sentence-transformer embeddings |
| 💊 **Treatment Recommendations** | Evidence-based therapy from ACG / AGA / ASGE guidelines |
| 📄 **PDF Report Generation** | Structured clinical reports via Gemini LLM + ReportLab |
| 👤 **Patient Management** | Full CRUD for patient records with analysis history |
| 🔐 **JWT Authentication** | Secure login/signup with bcrypt password hashing |
| 📈 **Analytics Dashboard** | ECharts visualizations for diagnosis trends and history |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                       │
│   Login │ Dashboard │ Patients │ Analyze │ Reports │ History    │
└──────────────────────────┬──────────────────────────────────────┘
                           │  REST API (Axios)
┌──────────────────────────▼──────────────────────────────────────┐
│                       FastAPI Backend                           │
│                                                                 │
│   Auth Routes │ Patient Routes │ Analysis Routes │ Report Routes│
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Vision Pipeline                       │   │
│  │   Preprocessing → Swin Transformer → Grad-CAM → Severity │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────────┐   │
│  │           LangGraph Agentic Orchestrator (6 Nodes)       │   │
│  │  Diagnosis → Query Builder → RAG Retrieval → Reranker    │   │
│  │          → Report Generation (Gemini) → Validation       │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                  │
│   ┌──────────────────┐  ┌────▼─────────────────────────────┐    │
│   │  SQLite/SQLAlch. │  │  FAISS Index + Sentence Embeddings│    │
│   └──────────────────┘  └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏥 Supported Conditions

| Condition | Clinical Details |
|---|---|
| **Normal Mucosa** | Healthy GI mucosa — no intervention required |
| **Gastric Ulcer** | Mucosal erosion; H. pylori & NSAID risk assessment (Forrest classification) |
| **Esophagitis** | Reflux-induced inflammation; Los Angeles classification grading |
| **Colon Polyp** | Mucosal protrusions; polypectomy & adenoma surveillance workflow |
| **Barrett's Esophagus** | Intestinal metaplasia; RFA therapy & dysplasia surveillance |

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| **API Framework** | FastAPI 0.111 + Uvicorn |
| **AI Vision** | PyTorch 2.3, Swin Transformer (`timm`), Grad-CAM |
| **LLM / Report Gen** | Google Gemini 1.5 Flash (`google-generativeai`) |
| **Agentic Framework** | LangGraph 0.1.4 + LangChain Core |
| **RAG Embeddings** | `sentence-transformers` 3.0 + FAISS |
| **Image Processing** | OpenCV, Pillow, NumPy |
| **Database** | SQLite via SQLAlchemy 2.0 |
| **Authentication** | JWT (`python-jose`) + bcrypt (`passlib`) |
| **PDF Generation** | ReportLab 4.2 |
| **Model Hosting** | HuggingFace Hub |

### Frontend
| Layer | Technology |
|---|---|
| **Framework** | React 19 + Vite 8 |
| **Routing** | React Router DOM 6 |
| **HTTP Client** | Axios |
| **Charts** | ECharts + echarts-for-react |
| **Icons** | Lucide React |
| **Linting** | OXLint |

---

## 📁 Project Structure

```
Rag_Agent_for_endoscopy_image/
├── backend/
│   ├── app/
│   │   ├── agent/                  # Agentic AI tool definitions
│   │   │   ├── agent.py            # Main agent loop
│   │   │   ├── patient_tool.py     # Patient data retrieval tool
│   │   │   ├── prediction_tool.py  # Vision prediction tool
│   │   │   └── rag_tool.py         # RAG retrieval tool
│   │   ├── model/                  # Swin Transformer loader & inference
│   │   │   ├── model_loader.py     # HuggingFace model download & load
│   │   │   └── model_utils.py      # Grad-CAM, segmentation, severity
│   │   ├── rag/                    # RAG pipeline
│   │   │   ├── embeddings.py       # FAISS index builder (runs at startup)
│   │   │   ├── retriever.py        # Similarity search over knowledge base
│   │   │   └── knowledge/          # Curated GI clinical guideline documents
│   │   ├── routes/                 # FastAPI route handlers
│   │   │   ├── analysis_routes.py  # Image upload & full pipeline trigger
│   │   │   ├── auth_routes.py      # Login / signup endpoints
│   │   │   ├── patient_routes.py   # Patient CRUD endpoints
│   │   │   └── report_routes.py    # PDF report download endpoint
│   │   ├── database.py             # SQLAlchemy models & session management
│   │   ├── orchestrator.py         # LangGraph pipeline graph (6 nodes)
│   │   ├── pipeline.py             # Full vision processing pipeline
│   │   ├── pdf_gen.py              # PDF report generator (ReportLab)
│   │   ├── auth.py                 # JWT utilities
│   │   └── main.py                 # FastAPI app entry point & startup hooks
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx           # Authentication page
│   │   │   ├── Signup.jsx          # New user registration
│   │   │   ├── Dashboard.jsx       # Analytics & overview charts
│   │   │   ├── Patients.jsx        # Patient management
│   │   │   ├── Analyze.jsx         # Image upload & live analysis view
│   │   │   ├── Reports.jsx         # PDF report viewer/download
│   │   │   └── History.jsx         # Analysis history log
│   │   ├── components/             # Reusable UI components
│   │   ├── contexts/               # React context (auth state, etc.)
│   │   ├── lib/                    # Axios API client
│   │   ├── App.jsx                 # Root component & route definitions
│   │   └── main.jsx                # Entry point
│   ├── package.json
│   └── vite.config.js
├── samples/                        # Sample endoscopy images for testing
│   ├── colon_polyp.png
│   ├── esophagitis.png
│   ├── gastric_ulcer.png
│   └── normal_mucosa.png
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and npm
- **Git**
- A **Google Gemini API key** (free tier): [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- A **HuggingFace token** (for model download): [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

---

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/AI-developer-189/Rag_Agent_for_endoscopy_image.git
cd Rag_Agent_for_endoscopy_image/backend

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
# Fill in your API keys (see Environment Variables section below)

# 5. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **On first startup**, the system will:
> - Initialize the SQLite database schema
> - Download the Swin Transformer model from HuggingFace Hub
> - Build the FAISS RAG embedding index from the knowledge base

**Backend API:** http://localhost:8000  
**Interactive Docs (Swagger UI):** http://localhost:8000/docs

---

### Frontend Setup

```bash
# From the repository root
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

**Frontend UI:** http://localhost:5173

---

## 🔑 Environment Variables

Create a `backend/.env` file using `.env.example` as a template:

| Variable | Required | Description |
|---|---|---|
| `HF_TOKEN` | ✅ **Yes** | HuggingFace token for Swin Transformer model download |
| `JWT_SECRET` | ✅ **Yes** | Secret key for JWT token signing — change in production |
| `GEMINI_API_KEY` | ⚠️ Optional | Google Gemini API key for AI report generation |
| `LLM_MODEL` | ⚠️ Optional | Gemini model name (default: `gemini-1.5-flash`) |
| `FRONTEND_URL` | ⚠️ Optional | Frontend URL for CORS config (default: `http://localhost:5173`) |

> **Note:** If `GEMINI_API_KEY` is omitted, the system falls back to built-in evidence-based clinical report templates. All vision pipeline, RAG, and patient management features remain fully functional.

---

## 📡 API Reference

The full interactive documentation is at **http://localhost:8000/docs** (Swagger UI).

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Register a new clinician account |
| `POST` | `/auth/login` | Login — returns a JWT bearer token |

### Patients
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/patients` | List all patients |
| `POST` | `/patients` | Create a new patient record |
| `GET` | `/patients/{id}` | Get patient details |
| `PUT` | `/patients/{id}` | Update patient record |
| `DELETE` | `/patients/{id}` | Delete patient record |

### Analysis
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analysis/analyze` | Upload endoscopy image — runs full AI pipeline |
| `GET` | `/analysis/history` | Retrieve analysis history for all patients |
| `GET` | `/analysis/{id}` | Get a specific analysis result |

### Reports
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/reports/{analysis_id}` | Download generated PDF clinical report |

---

## 🤖 Agentic Pipeline

After the vision pipeline processes the uploaded image, a **6-node LangGraph orchestrator** produces the final clinical report:

```
 Image Upload & Vision Pipeline
 ──────────────────────────────
 1. Preprocessing      → Resize, normalize, blur/artifact detection
 2. Classification     → Swin Transformer → label + confidence score
 3. Grad-CAM           → Heatmap overlaid on original image
 4. Segmentation       → Binary mask → lesion coverage % + severity level

        ↓

 LangGraph Agentic Orchestrator
 ───────────────────────────────
 Node 1 │ Diagnosis Node      → Builds structured clinical summary text
 Node 2 │ Query Builder       → Formulates RAG search query from diagnosis
 Node 3 │ RAG Retrieval       → FAISS lookup: symptoms, complications, treatments
 Node 4 │ Evidence Reranker   → Scores and re-orders retrieved medical evidence
 Node 5 │ Report Generation   → Gemini LLM synthesizes full clinical JSON report
        │                        (falls back to evidence-based templates if no key)
 Node 6 │ Validation Node     → Safety rule checks + metadata attachment

        ↓

 Structured Clinical Report (JSON → PDF via ReportLab)
```

---

## 📚 RAG Knowledge Base

The RAG pipeline uses **`all-MiniLM-L6-v2`** sentence embeddings and a **FAISS** vector index built at startup from curated GI clinical guidelines in `backend/app/rag/knowledge/`.

**Knowledge base covers:**
- ACG, AGA, and ASGE clinical practice guidelines
- Gastric ulcer management protocols (Forrest classification)
- Los Angeles classification for esophagitis grading
- Barrett's Esophagus Seattle biopsy protocol (4-quadrant biopsies every 2 cm)
- US Multi-Society Task Force colorectal polyp surveillance guidelines
- Upper GI bleeding management (JAMA, Am J Gastroenterol references)

---

## 🐳 Docker Deployment

A `Dockerfile` is provided for containerized backend deployment:

```bash
# Build the Docker image
cd backend
docker build -t endoscopy-cdss-backend .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e HF_TOKEN=your_huggingface_token \
  -e JWT_SECRET=your_jwt_secret \
  -e GEMINI_API_KEY=your_gemini_key \
  --name endoscopy-cdss \
  endoscopy-cdss-backend
```

---

## 🖼️ Sample Images

The `samples/` directory contains test images for each supported condition:

| File | Condition | Use |
|---|---|---|
| `normal_mucosa.png` | Normal healthy mucosa | Baseline / negative test |
| `gastric_ulcer.png` | Gastric ulcer | Ulcer detection test |
| `esophagitis.png` | Esophagitis | Reflux disease test |
| `colon_polyp.png` | Colon polyp | Polyp detection test |

Upload any file via the **Analyze** page in the frontend UI to run the full end-to-end pipeline.

---

## ⚠️ Medical Disclaimer

> This system is intended **for research and educational purposes only**. It is **not a certified or regulated medical device** and must **not** be used as a substitute for professional medical advice, diagnosis, or clinical treatment. All outputs should be reviewed and validated by a qualified gastroenterologist or licensed clinician before clinical use.

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>Built for advancing AI-assisted endoscopy diagnostics 🏥</strong>
</div>
