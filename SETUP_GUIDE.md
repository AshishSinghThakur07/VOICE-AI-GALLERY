# Day 1 Setup Guide - AI Voice Agents Challenge

This guide will help you set up and run your voice agent for Day 1 of the challenge.

## Prerequisites

Before starting, make sure you have:

1. **Python 3.9+** with [uv](https://docs.astral.sh/uv/) package manager
2. **Node.js 18+** with [pnpm](https://pnpm.io/)
3. **LiveKit Server** - Install using:
   ```bash
   # macOS
   brew install livekit
   
   # Windows (using Chocolatey)
   choco install livekit
   
   # Or download from: https://docs.livekit.io/home/cli/cli-setup
   ```

## Step 1: Get API Keys

You'll need the following API keys:

1. **LiveKit** - Sign up at [LiveKit Cloud](https://cloud.livekit.io/) or use local server
2. **Murf Falcon TTS** - Get your API key from [Murf API](https://murf.ai/api/docs)
3. **Google Gemini** - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
4. **Deepgram** - Get your API key from [Deepgram](https://deepgram.com/)

## Step 2: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Create `.env.local` file (copy from `.env.example` if it exists, or create new):
   ```bash
   # Create .env.local file with the following content:
   ```

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

4. Download required models:
   ```bash
   uv run python src/agent.py download-files
   ```

## Step 3: Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Create `.env.local` file:
   ```env
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-livekit-server-url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

## Step 4: Running the Application

You have two options:

### Option A: Use the convenience script (Recommended)

From the root directory:
```bash
# Make script executable (if on macOS/Linux)
chmod +x start_app.sh
./start_app.sh
```

**Note:** On Windows, you'll need to run the services manually (see Option B).

### Option B: Run services individually

Open three separate terminals:

**Terminal 1 - LiveKit Server:**
```bash
livekit-server --dev
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

## Step 5: Access the Application

1. Open your browser and navigate to: `http://localhost:3000`
2. Click "Start call" to begin a conversation with your voice agent
3. Allow microphone permissions when prompted
4. Start talking to your agent!

## Troubleshooting

### Backend Issues

- **Missing dependencies**: Run `uv sync` again
- **Model download fails**: Check your internet connection and try `uv run python src/agent.py download-files` again
- **API key errors**: Verify all API keys are correct in `.env.local`

### Frontend Issues

- **Dependencies not installed**: Run `pnpm install` again
- **Connection errors**: Verify LiveKit credentials in `.env.local` match the backend
- **Port 3000 already in use**: Change the port in `package.json` or stop the process using port 3000

### LiveKit Server Issues

- **Server won't start**: Make sure LiveKit CLI is installed correctly
- **Connection refused**: Verify the `LIVEKIT_URL` in both backend and frontend `.env.local` files

## Next Steps

Once your agent is running:

1. ✅ Have a brief conversation with your agent
2. ✅ Record a short video of your session
3. ✅ Post the video on LinkedIn with:
   - Description of what you did for Day 1
   - Mention you're building a voice agent using the fastest TTS API - **Murf Falcon**
   - Mention you're part of the **"Murf AI Voice Agent Challenge"**
   - Tag the official Murf AI handle
   - Use hashtags: **#MurfAIVoiceAgentsChallenge** and **#10DaysofAIVoiceAgents**
4. ✅ Submit your work: https://forms.gle/ge58Ne66wfPN98Pg7

## Resources

- [Murf Falcon TTS Documentation](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Challenge Repository](https://github.com/murf-ai/ten-days-of-voice-agents-2025)

Good luck with Day 1! 🚀


