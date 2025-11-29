// API Configuration
// For local development, use: http://localhost:8000
// For production, replace with your deployed backend URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? "http://localhost:8000/api/tasks"
  : "https://YOUR-BACKEND-URL.onrender.com/api/tasks";

