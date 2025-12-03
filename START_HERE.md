# 🚀 Ready to Start!

Your API keys are configured! Now let's get your voice agent running.

## Quick Start Options

### Option 1: Use the PowerShell Script (Easiest)

```powershell
.\start_app.ps1
```

This will open separate windows for:
- LiveKit Server (if installed locally)
- Backend Agent
- Frontend App

### Option 2: Manual Start (3 Terminals)

**Terminal 1 - LiveKit Server** (Skip if using LiveKit Cloud):
```powershell
livekit-server --dev
```

**Terminal 2 - Backend Agent**:
```powershell
cd backend
uv run python src/agent.py dev
```

**Terminal 3 - Frontend**:
```powershell
cd frontend
pnpm dev
```

## After Starting

1. **Wait for all services to start** (you'll see "Ready" messages)
2. **Open your browser** and go to: **http://localhost:3000**
3. **Click "Start call"** button
4. **Allow microphone access** when prompted
5. **Start talking** to your voice agent! 🎙️

## What to Test

- ✅ Agent responds to your voice
- ✅ Agent speaks back using Murf Falcon TTS
- ✅ Conversation flows naturally
- ✅ Transcription appears on screen

## Recording Your Video

Once everything works:
1. Record a 1-2 minute video showing:
   - The app running
   - You having a conversation
   - The agent responding
2. Post on LinkedIn with:
   - Description of Day 1
   - Mention "fastest TTS API - Murf Falcon"
   - Tag @Murf AI
   - Hashtags: #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents
3. Submit: https://forms.gle/ge58Ne66wfPN98Pg7

## Troubleshooting

**Backend won't start?**
- Check that all API keys are correct in `backend/.env.local`
- Make sure you're in the backend directory
- Check for error messages in the terminal

**Frontend won't start?**
- Check that LiveKit credentials match backend
- Make sure port 3000 is available
- Check for error messages in the terminal

**Can't connect?**
- Verify `LIVEKIT_URL` is correct (should start with `wss://`)
- Make sure LiveKit server is running (or using Cloud)
- Check that all three services are running

**Need help?** Check `SETUP_GUIDE.md` for detailed troubleshooting.

---

Ready? Let's start! 🚀


