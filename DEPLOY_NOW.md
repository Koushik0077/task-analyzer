# 🚀 Deploy Now - Step by Step

## IMPORTANT: I cannot deploy to external services without your accounts
## But I've prepared everything! Follow these steps:

---

## Step 1: Deploy Backend to Render (5 minutes)

### A. Create Render Account
1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest) or email

### B. Deploy Backend
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository (or use "Public Git repository")
   - If using GitHub: Authorize Render → Select your repo
   - If manual: You'll need to upload files
3. **Configure the service:**
   - **Name**: `task-analyzer-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```
     gunicorn task_analyzer.wsgi:application --bind 0.0.0.0:$PORT
     ```
4. **Add Environment Variables** (Click "Advanced"):
   - `SECRET_KEY`: Generate one by running in your terminal:
     ```powershell
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
     Copy the output and paste as value
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: Leave empty (Render auto-sets)
5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment
7. **Copy your backend URL** (e.g., `https://task-analyzer-backend.onrender.com`)

---

## Step 2: Update Frontend Configuration

1. **Edit `frontend/config.js`**
2. Replace this line:
   ```javascript
   : "https://YOUR-BACKEND-URL.onrender.com/api/tasks";
   ```
   With your actual Render URL:
   ```javascript
   : "https://task-analyzer-backend.onrender.com/api/tasks";
   ```
3. **Save the file**

---

## Step 3: Deploy Frontend to Netlify (2 minutes)

### A. Create Netlify Account
1. Go to: https://netlify.com
2. Click "Sign up" (free)
3. Sign up with GitHub (easiest) or email

### B. Deploy Frontend
**Option 1: Drag & Drop (Easiest)**
1. In Netlify dashboard, find **"Sites"**
2. Drag the entire `frontend` folder onto Netlify
3. Wait 30 seconds
4. **Copy your frontend URL** (e.g., `https://amazing-app-123.netlify.app`)

**Option 2: GitHub Deploy**
1. Click "Add new site" → "Import an existing project"
2. Connect GitHub → Select your repository
3. **Build settings:**
   - **Base directory**: `frontend`
   - **Build command**: (leave empty - it's static)
   - **Publish directory**: `frontend`
4. Click "Deploy site"
5. Wait 1-2 minutes
6. **Copy your frontend URL**

---

## Step 4: Test Your Deployment

1. Open your frontend URL in browser
2. Try adding a task
3. Click "Run Analysis"
4. Should work! 🎉

---

## Alternative: Quick Test Locally

If you want to test before deploying:

**Terminal 1 (Backend):**
```powershell
cd backend
.\venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
python -m http.server 5500
```

Then open: http://localhost:5500

---

## Need Help?

- **Backend not working?** Check Render logs
- **CORS errors?** Make sure `config.js` has correct backend URL
- **404 errors?** Check that backend is deployed and running

---

## Your Final URLs Will Be:

- **Backend**: `https://your-backend-name.onrender.com`
- **Frontend**: `https://your-frontend-name.netlify.app`

**Share the frontend URL with recruiters!** 🚀

