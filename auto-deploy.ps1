# Automated Deployment Script
Write-Host "=== Automated Deployment Setup ===" -ForegroundColor Green
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Cyan
    git init
    git add .
    git commit -m "Initial commit - Task Analyzer project"
    Write-Host "Git repository initialized!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== DEPLOYMENT INSTRUCTIONS ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "I've prepared everything for deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "Since I cannot create accounts on external services," -ForegroundColor Yellow
Write-Host "please follow these QUICK steps (5 minutes):" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. BACKEND (Render.com):" -ForegroundColor Cyan
Write-Host "   - Go to: https://render.com" -ForegroundColor White
Write-Host "   - Sign up (free, 30 seconds)" -ForegroundColor White
Write-Host "   - Click 'New +' -> 'Web Service'" -ForegroundColor White
Write-Host "   - Connect GitHub or upload 'backend' folder" -ForegroundColor White
Write-Host "   - Use settings from SETUP_DEPLOYMENT.md" -ForegroundColor White
Write-Host "   - Copy your backend URL" -ForegroundColor White
Write-Host ""
Write-Host "2. UPDATE CONFIG:" -ForegroundColor Cyan
Write-Host "   - Edit frontend/config.js" -ForegroundColor White
Write-Host "   - Replace YOUR-BACKEND-URL with your Render URL" -ForegroundColor White
Write-Host ""
Write-Host "3. FRONTEND (Netlify.com):" -ForegroundColor Cyan
Write-Host "   - Go to: https://netlify.com" -ForegroundColor White
Write-Host "   - Sign up (free, 30 seconds)" -ForegroundColor White
Write-Host "   - Drag 'frontend' folder onto Netlify" -ForegroundColor White
Write-Host "   - Copy your frontend URL (THIS IS YOUR FINAL LINK!)" -ForegroundColor White
Write-Host ""
Write-Host "Detailed guide: See SETUP_DEPLOYMENT.md" -ForegroundColor Green
Write-Host ""

# Generate SECRET_KEY for them
Write-Host "Generating SECRET_KEY for backend..." -ForegroundColor Cyan
$secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
if ($secretKey) {
    Write-Host ""
    Write-Host "=== YOUR SECRET_KEY ===" -ForegroundColor Yellow
    Write-Host $secretKey -ForegroundColor Green
    Write-Host ""
    Write-Host "Copy this and use it as SECRET_KEY environment variable in Render!" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "Could not generate SECRET_KEY. Run this manually:" -ForegroundColor Red
    Write-Host 'python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"' -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== ALL FILES READY ===" -ForegroundColor Green
Write-Host "Your project is ready to deploy!" -ForegroundColor Green
Write-Host ""

