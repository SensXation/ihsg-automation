# 🇮🇩 IHSG Automation Project

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Supabase-Database-green?style=for-the-badge&logo=supabase&logoColor=white)
![Status](https://img.shields.io/badge/Status-Automated-success?style=for-the-badge)

<br />

<div align="center">
  <h3>🟢 LIVE DEMO</h3>
  <a href="https://ihsg-automation-sensxation.streamlit.app/">
    <img src="https://img.shields.io/badge/Click_Here_to_View_Dashboard-2ea44f?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Live Demo" />
  </a>
</div>

<br />

---

## 📝 About The Project
This project is an **automated data pipeline** that tracks stock prices from the Indonesian Stock Exchange (IHSG).

Instead of updating data manually, this system uses **GitHub Actions** to run a Python script every day at **5:00 PM WIB**. It automatically fetches new data, cleans it, saves it to a **Supabase (PostgreSQL)** database, and updates the **Streamlit** dashboard in real-time.

## ✨ Key Features
* **Automated:** Runs daily via Cron Job (GitHub Actions) without manual input.
* **Cloud Database:** Stores history securely in PostgreSQL (Supabase) with duplicate prevention.
* **Separation of Concerns:** Distinct logic for Backend (`data_processor.py`), Frontend (`dashboard.py`), and ETL (`etl_pipeline.py`).
* **Pro Visualization:** Features TradingView-style Candlestick charts, Volume analysis, and Moving Averages (MA50/MA200).
* **Mobile Friendly:** The dashboard is optimized for both desktop and phone screens.

## 🛠️ Built With
* **Python 3.11**
* **Streamlit** (Frontend Dashboard)
* **Plotly** (Interactive Financial Charts)
* **Supabase** (PostgreSQL Database)
* **GitHub Actions** (CI/CD Automation)
* **yfinance** (Data Source)

## 📂 Project Structure
```text
ihsg-automation/
├── .github/workflows/   # Automation scripts (Cron Job)
├── .streamlit/          # Configuration (Secrets)
├── dashboard.py         # Frontend (UI & Charts)
├── data_processor.py    # Backend (Data Logic & Query)
├── etl_pipeline.py      # ETL Script (Daily Update)
├── backfill.py          # Utility (Initial Data Loader)
└── requirements.txt     # Python Dependencies
