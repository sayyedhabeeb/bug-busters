# TalentMatch AI - Unified Startup Script
Write-Host "============================" -ForegroundColor Cyan
Write-Host "   UNIFIED SYSTEM STARTUP    " -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# 0. Clean cleanup
Write-Host "[0/2] Cleaning up..." -ForegroundColor Gray
Stop-Process -Name "node" -ErrorAction SilentlyContinue
Stop-Process -Name "python" -ErrorAction SilentlyContinue 

# 1. Start everything via main.py
Write-Host "`n[1/2] Starting Unified System (API 8000 + React 5173)..." -ForegroundColor Yellow
python main.py --start

Write-Host "`n🚀 SYSTEM IS LIVE!" -ForegroundColor Green
Write-Host "----------------------------------"
Write-Host "Modern UI: http://localhost:5173"
Write-Host "Backend API: http://localhost:8000"
Write-Host "----------------------------------"
