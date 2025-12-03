# 🚀 Quick Start Guide - Day 1

## Prerequisites Check ✅

- ✅ Python 3.9+ with `uv` installed
- ✅ Node.js 18+ with `pnpm` installed
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed
- ✅ Required models downloaded

## What You Need to Do Now

### 1. Get Your API Keys

You need 4 API keys:

1. **LiveKit** - Sign up at https://cloud.livekit.io/ (free tier available)
2. **Murf Falcon TTS** - Get from https://murf.ai/api/docs
3. **Google Gemini** - Get from https://aistudio.google.com/app/apikey
4. **Deepgram** - Get from https://deepgram.com/ (free tier available)

### 2. Create Environment Files

**Backend** (`backend/.env.local`):
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key_here
LIVEKIT_API_SECRET=your_secret_here
MURF_API_KEY=your_murf_key_here
GOOGLE_API_KEY=your_google_key_here
DEEPGRAM_API_KEY=your_deepgram_key_here
```

**Frontend** (`frontend/.env.local`):
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key_here
LIVEKIT_API_SECRET=your_secret_here
```

### 3. Start the Application

**Option A: Use the PowerShell script (Windows)**
```powershell
.\start_app.ps1
```

**Option B: Manual start (3 terminals)**

Terminal 1 - LiveKit Server (if using local):
```bash
livekit-server --dev
```

Terminal 2 - Backend:
```bash
cd backend
uv run python src/agent.py dev
```

Terminal 3 - Frontend:
```bash
cd frontend
pnpm dev
```

### 4. Test Your Agent

1. Open http://localhost:3000
2. Click "Start call"
3. Allow microphone access
4. Start talking! 🎙️

## 🎬 Recording Your Video

1. Record a short video (1-2 minutes) showing:
   - The application running
   - You having a conversation with the agent
   - The agent responding with voice

2. Post on LinkedIn with:
   - ✅ Description of Day 1 task
   - ✅ Mention "fastest TTS API - Murf Falcon"
   - ✅ Tag @Murf AI
   - ✅ Hashtags: #MurfAIVoiceAgentsChallenge #10DaysofAIVoiceAgents

3. Submit: https://forms.gle/ge58Ne66wfPN98Pg7

## 🆘 Need Help?

- Check [README.md](./README.md) for detailed instructions
- Check [SETUP_GUIDE.md](./SETUP_GUIDE.md) for troubleshooting
- Join the challenge Discord/community for support

Good luck! 🚀


