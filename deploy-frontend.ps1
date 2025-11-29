# Frontend Deployment Helper Script
Write-Host "=== Frontend Deployment Setup ===" -ForegroundColor Green

# Check if Node.js is installed
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js not found. Installing npx globally..." -ForegroundColor Yellow
}

# Option 1: Using Python HTTP Server (Simple)
Write-Host "`nStarting Python HTTP Server on port 5500..." -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:5500" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the server`n" -ForegroundColor Gray

cd frontend
python -m http.server 5500

