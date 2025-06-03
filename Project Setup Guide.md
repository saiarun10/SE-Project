# Project Setup Guide

This project consists of a **Flask** backend and a **Vue.js 3** frontend. Follow the instructions below to set up and run the project locally.

## Prerequisites
- **Python 3.8+** installed for the backend
- **Node.js 18+** and **npm** installed for the frontend
- **Git** for cloning the repository (optional)

## Project Structure
- `backend/`: Contains the Flask backend code
- `frontend/`: Contains the Vue.js 3 frontend code
- `.env`: Configuration file for the backend
- `.env.development`: Configuration file for the frontend

## Backend Setup (Flask)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   Ensure the `.env` file is configured with the correct database settings (e.g., `SQLALCHEMY_DATABASE_URI="sqlite:///database.db"`). Then run:
   ```bash
   python setup_db.py
   ```

6. **Run the Flask application**:
   ```bash
   python app.py
   ```
   The backend will be available at `http://localhost:5000` (or as specified in `.env.development`).

## Frontend Setup (Vue.js 3)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Configure the frontend**:
   Ensure the `.env.development` file contains the correct backend URL (e.g., `VITE_BASE_URL=http://localhost:5000`).

4. **Run the Vue.js development server**:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173` (or as specified in `.env.development`).

## Environment Configuration

- **Backend (.env)**:
  - `FLASK_ENV`: Set to `development` for local development.
  - `DEBUG`: Set to `True` for debugging.
  - `SECRET_KEY`: A secure key for Flask sessions.
  - `SECURITY_PASSWORD_SALT`: Salt for password hashing.
  - `SQLALCHEMY_DATABASE_URI`: Database connection string (e.g., `sqlite:///database.db`).
  - `SQLALCHEMY_TRACK_MODIFICATIONS`: Set to `False` to disable tracking.
  - `LOG_LEVEL` and `LOG_FILE`: Optional logging configuration.
  - `FRONTEND_URL`: URL of the frontend (e.g., `http://localhost:5173`).

- **Frontend (.env.development)**:
  - `VITE_BASE_URL`: Backend API URL (e.g., `http://localhost:5000`).

## Running the Project

1. Start the backend server (Flask) as described in the Backend Setup section.
2. Start the frontend development server (Vue.js) as described in the Frontend Setup section.
3. Access the application in your browser at `http://localhost:5173`.

## Notes
- Ensure both `.env` and `.env.development` files are correctly configured before running the application.
- If you encounter issues, verify that the backend and frontend ports match the configurations in the environment files.
- For production, update `FLASK_ENV` to `production` and adjust other settings as needed.