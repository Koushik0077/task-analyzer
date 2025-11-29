# Deployment Guide - Smart Task Analyzer

This guide will help you deploy the Smart Task Analyzer to production.

## Option 1: Deploy to Render.com (Recommended - Free Tier Available)

### Backend Deployment (Django API)

1. **Create a Render Account**
   - Go to https://render.com
   - Sign up for a free account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use manual deploy)

3. **Configure the Service**
   - **Name**: `task-analyzer-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn task_analyzer.wsgi:application --bind 0.0.0.0:$PORT`
   - **Root Directory**: `backend`

4. **Set Environment Variables**
   - `SECRET_KEY`: Generate a random key (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com` (Render will provide this)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Copy your backend URL (e.g., `https://task-analyzer-backend.onrender.com`)

### Frontend Deployment (Static Site)

1. **Update Frontend API URL**
   - Edit `frontend/script.js`
   - Change line 1: `const API_BASE = "YOUR_BACKEND_URL/api/tasks";`
   - Replace `YOUR_BACKEND_URL` with your Render backend URL

2. **Deploy to Netlify (Easiest)**
   - Go to https://netlify.com
   - Sign up for free account
   - Drag and drop the `frontend` folder to Netlify
   - Or connect GitHub and set build directory to `frontend`
   - Your site will be live at `https://random-name.netlify.app`

3. **Alternative: Deploy to Vercel**
   - Go to https://vercel.com
   - Import your repository
   - Set root directory to `frontend`
   - Deploy

---

## Option 2: Deploy Everything to Railway.app

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy Backend**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Set root directory to `backend`
   - Railway will auto-detect Python and install dependencies
   - Add environment variables:
     - `SECRET_KEY`: (generate one)
     - `DEBUG`: `False`
   - Railway will provide a URL like `https://your-app.up.railway.app`

3. **Update Frontend**
   - Edit `frontend/script.js` with Railway backend URL
   - Deploy frontend separately to Netlify/Vercel, or serve from Django

---

## Option 3: Serve Frontend from Django (Single Deployment)

1. **Update Django Settings**
   - Add to `settings.py`:
   ```python
   STATICFILES_DIRS = [BASE_DIR.parent / "frontend"]
   ```

2. **Update URLs**
   - Add to `urls.py`:
   ```python
   from django.views.generic import TemplateView
   from django.conf import settings
   from django.conf.urls.static import static
   
   urlpatterns += [
       path('', TemplateView.as_view(template_name='index.html')),
   ]
   urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
   ```

3. **Deploy to Render/Railway**
   - Follow backend deployment steps
   - Frontend will be served from the same domain

---

## Quick Deploy Script

After deployment, update the frontend API URL:

```javascript
// In frontend/script.js, line 1
const API_BASE = "https://your-backend-url.onrender.com/api/tasks";
```

---

## Testing Deployment

1. Backend: Visit `https://your-backend-url.onrender.com/api/tasks/analyze/` (should return 405 Method Not Allowed - this is correct for GET)
2. Frontend: Visit your frontend URL and test adding/analyzing tasks

---

## Troubleshooting

- **CORS Errors**: Make sure `CORS_ALLOW_ALL_ORIGINS = True` in settings.py
- **Static Files**: Run `python manage.py collectstatic` before deployment
- **Database**: SQLite works for demo, but consider PostgreSQL for production
- **Environment Variables**: Double-check all env vars are set correctly

---

## Free Hosting Options Summary

| Service | Backend | Frontend | Free Tier |
|---------|---------|----------|-----------|
| Render | ✅ | ✅ | 750 hours/month |
| Railway | ✅ | ✅ | $5 credit/month |
| Netlify | ❌ | ✅ | Unlimited |
| Vercel | ❌ | ✅ | Unlimited |
| Heroku | ✅ | ✅ | No longer free |

**Recommended**: Render for backend + Netlify for frontend (both free)

