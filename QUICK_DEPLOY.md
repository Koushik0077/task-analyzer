# 🚀 Quick Deployment Guide

## Fastest Way to Deploy (5 minutes)

### Step 1: Deploy Backend to Render.com

1. **Go to https://render.com** and sign up (free)

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository** (or upload manually)

4. **Configure:**
   - **Name**: `task-analyzer-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn task_analyzer.wsgi:application --bind 0.0.0.0:$PORT`

5. **Add Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - `SECRET_KEY`: Run this in terminal to generate:
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: Leave empty (Render will auto-set)

6. **Click "Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Copy your URL (e.g., `https://task-analyzer-api.onrender.com`)

---

### Step 2: Update Frontend API URL

1. **Edit `frontend/config.js`**
   - Replace `YOUR-BACKEND-URL.onrender.com` with your actual Render URL
   - Example: `https://task-analyzer-api.onrender.com/api/tasks`

2. **Save the file**

---

### Step 3: Deploy Frontend to Netlify

1. **Go to https://netlify.com** and sign up (free)

2. **Drag and drop the `frontend` folder** onto Netlify
   - Or click "Add new site" → "Deploy manually"
   - Upload the `frontend` folder

3. **Your site is live!**
   - Netlify will give you a URL like `https://amazing-app-123.netlify.app`

---

## ✅ Done!

- **Backend**: `https://your-backend.onrender.com`
- **Frontend**: `https://your-frontend.netlify.app`

**Test it**: Open your frontend URL and try adding/analyzing tasks!

---

## Alternative: Deploy Everything to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Railway auto-detects Python
5. Set root directory to `backend`
6. Add environment variables (same as Render)
7. Deploy!

---

## Need Help?

- Check `DEPLOYMENT.md` for detailed instructions
- Common issues:
  - CORS errors → Make sure backend URL is correct in `config.js`
  - 500 errors → Check Render logs for issues
  - Static files → Already handled by WhiteNoise

