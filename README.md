# 🇮🇩 IHSG Automation Project

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Automated-green)

---

## 📝 About The Project
This project is an **automated data pipeline** that tracks stock prices from the Indonesian Stock Exchange (IHSG).

Instead of updating data manually, this system uses **GitHub Actions** to run a Python script every day at 5:00 PM WIB. It automatically fetches new data, cleans it, saves it to a **Supabase** database, and updates the **Streamlit** dashboard in real-time.

## ✨ Key Features
* **Automated:** Runs daily without any manual input.
* **Cloud Database:** Stores history securely in PostgreSQL (Supabase).
* **Data Visualization:** Interactive charts and tables via Streamlit.
* **Mobile Friendly:** The dashboard is optimized for phone screens.

## 🛠️ Built With
* **Python** (Pandas, yfinance, SQLAlchemy)
* **GitHub Actions** (Automation/Cron Job)
* **Supabase** (Cloud Database)
* **Streamlit** (Frontend Dashboard)

## 🚀 How to Run Locally
1. Clone the repo:
   ```bash
   git clone [https://github.com/SensXation/ihsg-automation.git](https://github.com/SensXation/ihsg-automation.git)
   ```

   pip install -r requirements.txt
   
   streamlit run dashboard.py
