# 🚀 Project Setup Guide

This project consists of a **Flask** backend and a **Vue.js 3** frontend. Follow the instructions below to set up and run the project locally.

---

## ✅ Prerequisites

* **Python 3.8+** (for backend)
* **Node.js 18+** and **npm** (for frontend)
---

## 🔧 Backend Setup (Flask)

1. **Navigate to backend folder**:

   ```bash
   cd backend
   ```

2. **Create a virtual environment**:

   * Windows:

     ```bash
     python -m venv venv
     ```
   * macOS/Linux:

     ```bash
     python3 -m venv venv
     ```

3. **Activate the environment**:

   * Windows:

     ```bash
     .\venv\Scripts\activate
     ```
   * macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   Ensure `.env` is correctly set up (see below). Then run:

   ```bash
   python setup_db.py
   ```

6. **Run the Flask server**:

   ```bash
   python app.py
   ```

   The backend runs at: `http://localhost:5000`

---

## 🖥️ Frontend Setup (Vue.js 3)

1. **Navigate to frontend folder**:

   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:

   ```bash
   npm install
   ```

3. **Check `.env.development`**:

   ```env
   VITE_BASE_URL=http://localhost:5000
   ```

4. **Start the Vue dev server**:

   ```bash
   npm run dev
   ```

   The frontend will be live at: `http://localhost:5173`

---

## 🔐 Environment Configuration

### 📁 `.env` (Backend)

```env
# General Flask Config
FLASK_ENV=development
DEBUG=True
SECRET_KEY="thisissecret"
SECURITY_PASSWORD_SALT="thisissaltt"

# JWT Configuration
JWT_SECRET_KEY="jwtsecretkey"
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

# Database
SQLALCHEMY_DATABASE_URI="sqlite:///database.db"
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Logging (Optional)
LOG_LEVEL="INFO"
LOG_FILE="app.log"

# Frontend URL
FRONTEND_URL="http://localhost:5173"
```

### 📁 `.env.development` (Frontend)

```env
VITE_BASE_URL=http://localhost:5000
```

---

## 👥 Test User Credentials

### 👑 Admin Login

```json
{
  "username": "21f1001520",
  "email": "21f1001520@ds.study.iitm.ac.in",
  "password": "123456"
}
```

### 🙋 Regular User Login

```json
{
  "username": "shib",
  "email": "shibkumarsaraf2001@gmail.com",
  "password": "12345678"
}
```

---

## ▶️ Running the Full App

1. Start backend server (Flask):

   ```bash
   cd backend
   source venv/bin/activate  # or activate on Windows
   python app.py
   ```

2. Start frontend server (Vue):

   ```bash
   cd frontend
   npm run dev
   ```

3. Open browser:

   ```
   http://localhost:5173
   ```

---

## 📝 Notes

* Make sure `.env` and `.env.development` are present and properly configured.
* The backend (`http://localhost:5000`) and frontend (`http://localhost:5173`) should match your configs.
* For production, set `FLASK_ENV=production` and configure secure secrets and domains.
