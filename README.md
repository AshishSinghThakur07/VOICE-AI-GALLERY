# AI Voice Agents Challenge - Day 1 Setup

Welcome to Day 1 of the **AI Voice Agents Challenge** by [murf.ai](https://murf.ai)!

This repository contains a complete voice agent setup using **Murf Falcon** - the consistently fastest TTS API.

## ✅ Setup Status

- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed  
- ✅ Required models downloaded
- ⚠️ LiveKit server needs to be configured
- ⚠️ Environment variables need to be configured

## 🚀 Quick Start

### Step 1: Install LiveKit Server

You have two options:

#### Option A: Use LiveKit Cloud (Recommended for beginners)

1. Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
2. Create a new project
3. Get your credentials from the project dashboard
4. Use these credentials in your `.env.local` files

#### Option B: Install LiveKit Server Locally (Windows)

1. Download LiveKit server from: https://github.com/livekit/livekit/releases
2. Or use Docker:
   ```bash
   docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp -p 50000-50100:50000-50100/udp livekit/livekit-server --dev
   ```

### Step 2: Get Your API Keys

You'll need the following API keys:

1. **LiveKit** - From [LiveKit Cloud](https://cloud.livekit.io/) or use local server
2. **Murf Falcon TTS** - Get from [Murf API Dashboard](https://murf.ai/api/docs)
3. **Google Gemini** - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
4. **Deepgram** - Get from [Deepgram Dashboard](https://deepgram.com/)

### Step 3: Configure Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create `.env.local` file:
   ```env
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-livekit-server-url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret

   # Murf Falcon TTS API Key
   MURF_API_KEY=your_murf_api_key

   # Google Gemini API Key (for LLM)
   GOOGLE_API_KEY=your_google_api_key

   # Deepgram API Key (for STT)
   DEEPGRAM_API_KEY=your_deepgram_api_key
   ```

   **For LiveKit Cloud users**, you can automatically populate credentials:
   ```bash
   lk cloud auth
   lk app env -w -d .env.local
   ```

### Step 4: Configure Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Create `.env.local` file:
   ```env
   # LiveKit Configuration (same as backend)
   LIVEKIT_URL=wss://your-livekit-server-url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

### Step 5: Run the Application

Open **three separate terminals**:

**Terminal 1 - LiveKit Server:**
```bash
# If using LiveKit Cloud, skip this step
# If using local server:
livekit-server --dev

# Or with Docker:
docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp -p 50000-50100:50000-50100/udp livekit/livekit-server --dev
```

**Terminal 2 - Backend Agent:**
```bash
cd backend
uv run python src/agent.py dev
```

**Terminal 3 - Frontend:**
```bash
cd frontend
pnpm dev
```

### Step 6: Access the Application

1. Open your browser and navigate to: **http://localhost:3000**
2. Click **"Start call"** to begin a conversation
3. Allow microphone permissions when prompted
4. Start talking to your voice agent! 🎙️

## 📋 Day 1 Task Checklist

- [ ] ✅ Get the starter repo running end-to-end (backend + frontend)
- [ ] ✅ Successfully connect to the voice agent in your browser
- [ ] ✅ Have a brief conversation with the agent
- [ ] ✅ Record a short video of your session
- [ ] ✅ Post the video on LinkedIn with:
  - Description of what you did for Day 1
  - Mention you're building a voice agent using the **fastest TTS API - Murf Falcon**
  - Mention you're part of the **"Murf AI Voice Agent Challenge"**
  - Tag the official Murf AI handle
  - Use hashtags: **#MurfAIVoiceAgentsChallenge** and **#10DaysofAIVoiceAgents**
- [ ] ✅ Submit your work: https://forms.gle/ge58Ne66wfPN98Pg7

## 🛠️ Troubleshooting

### Backend Issues

- **Missing dependencies**: Run `cd backend && uv sync`
- **Model download fails**: Run `cd backend && uv run python src/agent.py download-files`
- **API key errors**: Verify all API keys are correct in `backend/.env.local`

### Frontend Issues

- **Dependencies not installed**: Run `cd frontend && pnpm install`
- **Connection errors**: Verify LiveKit credentials in `frontend/.env.local` match the backend
- **Port 3000 already in use**: Change the port in `frontend/package.json` or stop the process using port 3000

### LiveKit Server Issues

- **Server won't start**: 
  - Make sure LiveKit CLI is installed (or use Docker)
  - For LiveKit Cloud, verify your credentials are correct
- **Connection refused**: 
  - Verify the `LIVEKIT_URL` in both backend and frontend `.env.local` files
  - Make sure the URL format is correct (e.g., `wss://your-project.livekit.cloud`)

## 📚 Resources

- [Murf Falcon TTS Documentation](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Challenge Repository](https://github.com/murf-ai/ten-days-of-voice-agents-2025)
- [LiveKit Cloud](https://cloud.livekit.io/)
- [Setup Guide](./SETUP_GUIDE.md) - Detailed setup instructions

## 🎯 What's Next?

Once your agent is running and you've completed Day 1:

1. Share your video on LinkedIn
2. Submit your work through the form
3. Get ready for Day 2!

Good luck with the challenge! 🚀

---

**Built for the AI Voice Agents Challenge by murf.ai**
