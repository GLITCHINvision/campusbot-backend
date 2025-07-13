#  Fact-Checker RAG Chatbot

An AI-powered fact-checking chatbot that verifies user questions using:

-  LLMs (Hugging Face Transformers)
-  Real News (via NewsAPI)
-  Summarization (DistilBART / FalconsAI)
-  Voice Input + UI Enhancements

> Built using **React + Flask**, and deployed on **Vercel + Render** 

---

##  Features

-  Fact-check with voice or text
-  Toggle between "LLM" and "Verified Only" modes
-  Real-time summarization of trusted news
-  Dark/light theme toggle
-  Speech recognition (Mic support)
-  Deployed backend using Render
-  Frontend hosted on Vercel

---

##  Tech Stack

| Frontend           | Backend           | AI & APIs            |
|--------------------|-------------------|----------------------|
| React.js           | Flask (Python)    | HuggingFace Transformers |
| Vercel (hosting)   | Render (API)      | NewsAPI.org          |
| Axios, Mic, UI     | Gunicorn, CORS    | dotenv, summarizer   |

---

##  Setup Instructions

###  Backend (Flask on Render)

```bash
cd backend
pip install -r requirements.txt
python app.py


 Live Demo
 Frontend: https://factcheck-frontend.vercel.app/

 Backend: https://factcheck-backend-v2mt.onrender.com

