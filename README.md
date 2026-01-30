# 🚀 AI Recruiter Pro: Intelligent Resume Screening System

### **Simulating a Senior Technical Recruiter with Llama 3.3 70B**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![AI Model](https://img.shields.io/badge/AI-Llama_3.3_70B-purple)
![Framework](https://img.shields.io/badge/Frontend-Streamlit-red)

## 📌 Project Overview
**AI Recruiter Pro** is a semantic analysis engine designed to move beyond the "keyword counting" of traditional ATS. It simulates the reasoning of a human Senior Recruiter to evaluate candidates based on **context, potential, and transferable skills**.

Unlike basic wrappers, this system features a **"Hybrid Ingestion Engine"** that can read scanned documents (OCR) and an **"AI Gatekeeper"** that strictly validates files to prevent fraud or errors.

---

## 🔥 Key Innovations (New Features)

### 🛡️ 1. The "AI Gatekeeper" (Anti-Hallucination Layer)
* **Problem:** Standard AI apps will happily analyze a "Cooking Recipe" as if it were a Resume, giving it a score of 20/100.
* **Solution:** My system uses a pre-processing AI agent to **read and classify the document type** before analysis begins.
* **Result:** It instantly **rejects invalid files** (lyrics, recipes, homework) with a specific error message, ensuring data integrity.

### 👁️ 2. Hybrid OCR Engine (Scanned PDF Support)
* **Capability:** Integrated **Tesseract OCR** & **pdfplumber** to handle diverse formats.
* **Impact:** The system detects if a PDF is an image scan and automatically switches to Optical Character Recognition to extract the text, ensuring no candidate is ignored due to formatting.

### 💡 3. Implicit Skill Mapping
* **Logic:** Goes beyond exact matches. If a candidate lists *"Pandas, NumPy, and Scikit-Learn"*, the system credits them for **"Data Science"** (marked as an **Orange "Implicit" Pill**), even if they never wrote that exact phrase.

---

## 🧠 Core Capabilities

* **✅ Decision Logic:** Categorizes candidates into **PASS**, **BORDERLINE**, or **REJECT** with a weighted 0-100 ATS Score.
* **📉 Gap Analysis:** clearly distinguishes between "Critical Missing Skills" (Red) and nice-to-haves.
* **🎓 Career Coaching:** Generates actionable, role-specific advice for candidates to improve their profile (e.g., *"Build a project using Docker to fix your Containerization gap"*).

---

## 🛠️ Technical Architecture

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Inference Engine** | **Groq API (Llama 3.3 70B)** | Sub-3-second deep reasoning. |
| **Frontend** | **Streamlit** | Interactive dashboard & state management. |
| **Visuals** | **Plotly** | Real-time confidence gauge charts. |
| **OCR / Text** | **Tesseract & pdfplumber** | Hybrid text extraction pipeline. |
| **Validation** | **Pydantic / JSON Mode** | Strict schema enforcement for reliable data. |

---

## 🚀 How to Run Locally

### Prerequisites
* Python 3.11+
* Tesseract OCR installed on your machine.

### Installation Steps
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/shahidafridk/ai-recruiter-final.git](https://github.com/shahidafridk/ai-recruiter-final.git)
   cd ai-recruiter-final
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
3. **Set up API Keys: Create a .env file in the root directory and add:**
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
4. **Run the Application:**
   ```bash
   streamlit run ui/streamlit_app.py
---

## ⚠️ Disclaimer

**This project is a concept simulation developed for academic demonstration. While it uses advanced AI, recruitment decisions should always involve human judgment.**

---

© 2026 AI Recruiter Pro. MIT License.









