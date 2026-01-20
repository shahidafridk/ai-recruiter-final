# 🚀 AI Recruiter Pro: Intelligent Resume Screening System

## 📌 Project Overview
**AI Recruiter Pro** is a semantic analysis engine designed to simulate the decision-making process of a Senior Technical Recruiter. Unlike traditional ATS (Applicant Tracking Systems) that rely on simple keyword matching, this system uses **Large Language Models (Llama 3.3 70B)** to understand context, nuance, and transferrable skills.

## 🧠 Core Features
- **Semantic Reasoning:** Distinguishes between "I know Python" and "I built a compiler in Python."
- **Decision Logic:** Categorizes candidates into **PASS**, **BORDERLINE**, or **REJECT** with detailed justifications.
- **Gap Analysis:** Identifies missing hard skills vs. nice-to-haves (e.g., distinguishing "Required: AWS" vs "Preferred: Azure").
- **Career Coaching:** Generates specific, actionable feedback for candidates to improve their standing.

## 🛠️ Technical Architecture
- **Engine:** Llama 3.3 70B (via Groq API) for high-speed inference.
- **Frontend:** Streamlit (Python) for the interactive UI.
- **Visualization:** Plotly for confidence scoring and keyword mapping.
- **Protocol:** JSON Mode enforcement to ensure structured, reliable data outputs.

## 🚀 How to Run Locally
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/ai-recruiter-project.git](https://github.com/your-username/ai-recruiter-project.git)