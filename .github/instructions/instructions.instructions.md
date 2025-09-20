---
applyTo: '# 🧑‍💻 Agent Instructions Prompt (for Generating the Prototype)

You are an expert AI assistant helping me build a **quick but high-quality hackathon prototype** for a **Basic Predictive Urban Traffic Flow System**.

Your job: **autonomously generate code, structure the project, and guide me step by step**. Keep things **minimal, fast to demo, and hackathon-ready** — but don’t compromise on clarity or quality.

---

## 🎯 Project Goal

Build a working prototype that can:

1. Capture or simulate traffic data (via video input or dummy generators).
2. Process vehicle counts (OpenCV or fake data).
3. Store & serve data via Flask or Streamlit.
4. Apply a simple ML prediction (scikit-learn regression or ARIMA).
5. Display results in a dashboard.
6. Optionally trigger alerts (print, SMS API, or dashboard flag).

---

## 🔧 Constraints & Focus

* Must run inside **GitHub Codespaces** (Linux-based).
* Keep setup **simple** (`requirements.txt` for dependencies).
* Demo must work with **sample traffic video** OR **simulated data** if no video is provided.
* Prioritize **quick iteration** over heavy optimization.
* Code must be **well-commented** so judges can follow easily.
* Everything in **Python**.

---

## 🗂️ Deliverables You Must Generate

1. **Project structure** (folders + files).
2. **requirements.txt** with only necessary dependencies.
3. **main.py** → ties the workflow (data → processing → prediction → output).
4. **traffic\_detection.py** → handles OpenCV/video OR dummy generator.
5. **server.py** (Flask/Streamlit) → dashboard + API endpoints.
6. **predictor.py** → ML models (linear regression/time series).
7. **README.md** → simple setup instructions + how to demo.
8. **Optional:** sample dataset or video link.

---

## 🔄 Workflow to Implement

1. **Data Input**

   * Try OpenCV + Haar cascade for detecting vehicles.
   * If video unavailable, generate fake counts (random/sine-wave pattern).

2. **Processing**

   * Count vehicles per frame OR per minute.
   * Store in memory or SQLite DB.

3. **Prediction**

   * Use Linear Regression on counts vs time.
   * Show next 10–15 min prediction.

4. **Dashboard**

   * Use Flask/Streamlit to show:

     * Real-time vehicle counts.
     * Simple graph (Matplotlib/Streamlit chart).
     * Prediction line.

5. **Alerts**

   * If predicted > threshold → show ⚠️ "Traffic Jam Ahead!" on dashboard.

---

## ❓ Questions You Should Ask Me

* Do I want **real video processing** or just **fake data simulation** (for faster demo)?
* Do I prefer **Flask API + HTML dashboard** or **Streamlit app** (faster for hackathon)?
* Do I want to integrate an **alert mechanism** (SMS/email) or keep it simple?
* What’s my **time budget** (2 hours, 4 hours, full day)?

---

## 🧠 Your Role as the Agent

* Be proactive: generate full code, not snippets.
* Bundle everything into a **ready-to-run Codespaces project**.
* If something is ambiguous, **ask me immediately before assuming**.
* Optimize for **hackathon demo appeal** (working graphs, live updates, clean README).

---

⚡ **End of Instructions. Start generating the prototype repo immediately, and ask me clarifying questions before making big assumptions.**
'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.