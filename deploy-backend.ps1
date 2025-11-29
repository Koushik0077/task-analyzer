# Backend Deployment Helper Script
Write-Host "=== Backend Deployment Setup ===" -ForegroundColor Green

cd backend

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\activate

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

# Run migrations
Write-Host "Running migrations..." -ForegroundColor Cyan
python manage.py migrate

# Start server
Write-Host "`nStarting Django server..." -ForegroundColor Cyan
Write-Host "Backend API available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the server`n" -ForegroundColor Gray

python manage.py runserver

