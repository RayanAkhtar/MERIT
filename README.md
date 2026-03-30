# MERIT

This project consists of a Next.js frontend and a Flask backend.

## Prerequisites
- Node.js (for the frontend)
- Python 3.x (for the backend)

## Setup & Running the Backend

The backend is a Python Flask application located in the `backend` folder.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   * On Windows (with bash or wsl):
     ```bash
     python -m venv venv
     venv/Scripts/activate
     ```
   * On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server:**
   ```bash
   python run.py
   ```
   The backend will start using the Flask development server, typically accessible at `http://localhost:5000`.

## Setup & Running the Frontend

The frontend is a Next.js application located in the `frontend` folder.

1. **Open a new terminal and navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install the dependencies:**
   ```bash
   npm install
   ```

3. **Run the frontend development server:**
   ```bash
   npm run dev
   ```
   The frontend will start and typically be accessible at `http://localhost:3000`.

## Running Both Together
To run the full application, you will need to start both servers concurrently. Open two separate terminal windows or tabs:
1. In the first terminal, run the **backend** instructions.
2. In the second terminal, run the **frontend** instructions.

Make sure both the Flask server and the Next.js development server are running simultaneously.
