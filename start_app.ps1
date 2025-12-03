# Windows PowerShell script to start all services
# Run this from the root directory: .\start_app.ps1

Write-Host "Starting AI Voice Agent Application..." -ForegroundColor Green
Write-Host ""

# Check if LiveKit server is available
$livekitAvailable = Get-Command livekit-server -ErrorAction SilentlyContinue

if (-not $livekitAvailable) {
    Write-Host "⚠️  LiveKit server not found locally." -ForegroundColor Yellow
    Write-Host "   If you're using LiveKit Cloud, you can skip this step." -ForegroundColor Yellow
    Write-Host "   Otherwise, install LiveKit server or use Docker:" -ForegroundColor Yellow
    Write-Host "   docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp -p 50000-50100:50000-50100/udp livekit/livekit-server --dev" -ForegroundColor Cyan
    Write-Host ""
    $useCloud = Read-Host "Are you using LiveKit Cloud? (y/n)"
    if ($useCloud -ne "y") {
        Write-Host "Please start LiveKit server manually or use Docker, then run this script again." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Starting LiveKit server..." -ForegroundColor Cyan
    Start-Process -NoNewWindow livekit-server -ArgumentList "--dev"
    Start-Sleep -Seconds 3
}

# Start backend
Write-Host "Starting backend agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; uv run python src/agent.py dev"

# Wait a bit for backend to start
Start-Sleep -Seconds 2

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; pnpm dev"

Write-Host ""
Write-Host "✅ All services starting!" -ForegroundColor Green
Write-Host "   Backend: Running in separate window" -ForegroundColor White
Write-Host "   Frontend: Running in separate window" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Open http://localhost:3000 in your browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit (services will continue running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


