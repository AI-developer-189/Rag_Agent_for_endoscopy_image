# 🔬 Explainable DINOv2–Swin AI Endoscopy Clinical Decision Support System

> **An explainable Agentic AI platform for gastrointestinal endoscopy image analysis powered by CycleGAN, ESRGAN, DINOv2, Swin Transformer, Grad-CAM++, RAG, and clinical reasoning — supporting structured diagnostic reports and risk assessment.**

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
| 🖼️ **Image Classification** | DINOv2–Swin Fusion Transformer for 8 GI classes |
| 🔥 **Grad-CAM++ Heatmaps** | Visual explanations highlighting lesion regions of interest |
| 📊 **Severity Assessment** | Agentic AI-based risk assessment and clinical recommendations |
| 🤖 **Agentic Orchestration** | LangGraph-based clinical reasoning and report-generation pipeline |
| 📚 **RAG Pipeline** | FAISS-indexed knowledge base with sentence-transformer embeddings |
| 💊 **Treatment Recommendations** | Evidence-based therapy from ACG / AGA / ASGE guidelines |
| 📄 **PDF Report Generation** | Structured clinical reports via Gemini LLM + ReportLab |
| 👤 **Patient Management** | Full CRUD for patient records with analysis history |
| 🔐 **JWT Authentication** | Secure login/signup with bcrypt password hashing |
| 📈 **Analytics Dashboard** | ECharts visualizations for diagnosis trends and history |

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                          │
│        Login │ Dashboard │ Patients │ Analyze │ Reports │ History │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────────────┐
│                         FastAPI Backend                            │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 GI Vision Pipeline                           │  │
│  │                                                              │  │
│  │ GI Image → CycleGAN → ESRGAN → Enhanced Image                │  │
│  │                         │                                    │  │
│  │              ┌──────────┴──────────┐                         │  │
│  │              ▼                     ▼                         │  │
│  │          DINOv2                  Swin-Tiny                    │  │
│  │      Global Semantic       Local / Multi-scale                │  │
│  │         Features               Features                       │  │
│  │              └──────────┬──────────┘                         │  │
│  │                         ▼                                    │  │
│  │                 Token Fusion                                 │  │
│  │                         ▼                                    │  │
│  │              Fusion Transformer                              │  │
│  │                   (2 Layers)                                 │  │
│  │                         ▼                                    │  │
│  │               Global Pooling                                 │  │
│  │                         ▼                                    │  │
│  │                 Gated Fusion                                 │  │
│  │                         ▼                                    │  │
│  │            Classification + Softmax                          │  │
│  │                         ▼                                    │  │
│  │                  8 GI Classes                                │  │
│  │                         │                                    │  │
│  │                         ▼                                    │  │
│  │                    Grad-CAM++                                │  │
│  └─────────────────────────┬────────────────────────────────────┘  │
│                            │                                       │
│  ┌─────────────────────────▼────────────────────────────────────┐  │
│  │             Agentic AI Clinical Intelligence Layer           │  │
│  │                                                              │  │
│  │ Prediction + Confidence + Heatmap + Patient Context         │  │
│  │                         │                                    │  │
│  │                         ▼                                    │  │
│  │          RAG / Clinical Guidelines Retrieval                 │  │
│  │                         │                                    │  │
│  │                         ▼                                    │  │
│  │             Clinical Reasoning Agent                         │  │
│  │                         │                                    │  │
│  │                         ▼                                    │  │
│  │          Risk & Recommendation Agent                         │  │
│  │                         │                                    │  │
│  │                         ▼                                    │  │
│  │                 Report Generation                            │  │
│  └─────────────────────────┬────────────────────────────────────┘  │
│                            │                                       │
│          ┌─────────────────┴─────────────────┐                    │
│          ▼                                   ▼                    │
│   SQLite / SQLAlchemy                 FAISS + Embeddings          │
│   Patient / Result Data               Clinical Knowledge Base     │
└────────────────────────────────────────────────────────────────────┘
```

### Core Vision Architecture

```text
Enhanced GI Image
       │
       ├──────────────► DINOv2 ViT-S/14 ─► 384-D Patch Features
       │                                      │
       │                                  Linear 256-D
       │                                      │
       └──────────────► Swin-Tiny ─────────► 768-D Patch Features
                                              │
                                          Linear 256-D
                                              │
                       ┌──────────────────────┘
                       ▼
                  Token Fusion
                       ▼
              Fusion Transformer
                  (2 Layers)
                       ▼
                 Global Pooling
                       ▼
                  Gated Fusion
                       ▼
              Classification Head
                       ▼
                    Softmax
                       ▼
                8 GI Classes
```

> **Model status:** The DINOv2–Swin Fusion Transformer is the proposed classification architecture. If the currently deployed inference service still uses the Swin-Tiny-only checkpoint, describe that checkpoint separately from the proposed fusion model until the fusion checkpoint is trained and deployed.

---

## 🏥 Supported Conditions

The revised classification setup currently defines **8 gastrointestinal classes**:

| Class | Description |
|---|---|
| **Dyed-Lifted Polyps** | Polyp images after dye-assisted lifting |
| **Dyed-Resection Margins** | Images of dyed resection margins |
| **Esophagitis** | Inflammatory changes of the esophageal mucosa |
| **Normal Cecum** | Normal cecal anatomy |
| **Normal Pylorus** | Normal pyloric anatomy |
| **Normal Z-Line** | Normal gastroesophageal junction / Z-line |
| **Polyps** | Gastrointestinal polyp images |
| **Ulcerative Colitis** | Endoscopic manifestations associated with ulcerative colitis |

The final clinical-support output is intended to include the predicted class, confidence, visual explanation, risk assessment, and recommendations.

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| **API Framework** | FastAPI 0.111 + Uvicorn |
| **AI Vision** | PyTorch, DINOv2, Swin Transformer, Grad-CAM++ |
| **Image Enhancement** | CycleGAN + ESRGAN |
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
> - Load the configured vision model/checkpoint from HuggingFace Hub
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

The Agentic AI layer extends the vision model from image classification to structured clinical decision support.

```text
GI Endoscopic Image
        │
        ▼
CycleGAN → ESRGAN
        │
        ▼
DINOv2 + Swin Fusion Transformer
        │
        ├── Disease Prediction
        ├── Confidence Score
        └── Grad-CAM++ Heatmap
        │
        ▼
Agentic AI Orchestrator
        │
        ├── Perception / Prediction
        ├── Explanation
        ├── Clinical Reasoning
        ├── RAG Clinical Guideline Retrieval
        ├── Risk & Recommendation
        └── Structured Report Generation
        │
        ▼
Clinical-Support Report
```

### Structured Output

- Predicted gastrointestinal abnormality
- Confidence score and confidence reasoning
- Grad-CAM++ heatmap / explanation
- Relevant clinical evidence
- Risk assessment
- Potential overlooked high-risk conditions
- Follow-up / treatment recommendations
- Structured PDF report

All outputs are intended for research and clinical decision support; final interpretation remains with a qualified clinician.

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
  <strong>Built for explainable and AI-assisted endoscopy clinical decision support 🏥</strong>
</div>
