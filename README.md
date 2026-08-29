# Pyrix — Multi-Company Operations & Settings Suite

Pyrix is an enterprise modern operations and settings web application built with **FastAPI**, **Jinja2**, and **Microsoft SQL Server**.

---

## 🚀 Features

- **Multi-Company Operations & Switcher**: Dynamically switch between companies and organizations.
- **Enterprise Modules & Monographs**:
  - System Overview & Diagnostics
  - Dynamic Form & Table Builder
  - SQL Inspector & Schema Management
  - Manufacturing Operations & Workflow Engine
  - Audit Logging & Session Tracking
- **Authentication & Security**:
  - Session Inactivity Guard (1-hour timeout)
  - Cookie-based authentication & route protection
- **Modern UI**: Clean macOS / Windows 11 Fluent inspired design.

---

## 🛠️ Requirements & Prerequisites

- **Python**: 3.10+
- **Microsoft SQL Server**: 2019 / 2022 / 2025
- **ODBC Driver 18 for SQL Server**

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tsalmanrahman/pyrix.git
   cd pyrix
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv env
   # On Windows:
   .\env\Scripts\activate
   # On Linux/macOS:
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update database credentials and host in `.env`.

5. **Run the application:**
   ```bash
   python run.py
   ```
   Or with Uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access in browser:**
   Open [http://localhost:8000](http://localhost:8000)
