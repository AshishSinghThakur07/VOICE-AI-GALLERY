# Deployment Guide for Voice Agent Portfolio

## 1. Project Status
Based on the codebase, the following days are implemented:
- **Day 1 - 9**: Existing agents found in `backend/src/agents/`.
- **Day 10**: Implemented by us (`day10_improv.py`).

## 2. Deployment Architecture
This application has two parts that need to be deployed separately:

### A. Frontend (Next.js)
- **Where to deploy**: **Vercel** (Best & Free for personal use).
- **Why**: Native support for Next.js, global CDN, easy setup.
- **How**:
  1. Push your code to the GitHub repository.
  2. Go to Vercel Dashboard -> "Add New..." -> "Project".
  3. Import your `VOICE-AI-GALLERY` repository.
  4. **CRITICAL STEP**: In the "Configure Project" screen:
     - **Root Directory**: Click "Edit" and select `frontend`.
     - **Framework Preset**: It should automatically detect "Next.js" after you change the root directory. If not, select "Next.js".
  5. **Environment Variables**: Expand the section and add:
     - `LIVEKIT_API_KEY`: Your API Key (from LiveKit Cloud).
     - `LIVEKIT_API_SECRET`: Your API Secret (from LiveKit Cloud).
     - `LIVEKIT_URL`: Your LiveKit Cloud URL (wss://...).
  6. Click **Deploy**.

### B. Backend (Python Agent)
- **Where to deploy**: **Fly.io** or **Railway** (Free tiers/Trial available).
- **Why**: The agent needs to run **continuously** (long-running process) to listen for users. Vercel *cannot* host this because Vercel functions time out after a few seconds.
- **How**:
  1. You need to deploy the Docker container defined in `backend/Dockerfile`.
  2. **Fly.io Example**:
     - Install `flyctl`.
     - Run `fly launch` in the `backend` folder.
     - Set secrets: `fly secrets set LIVEKIT_URL=... LIVEKIT_API_KEY=...` etc.
     - Deploy: `fly deploy`.

## 3. Cost Warning ⚠️
**Crucial for Portfolios**:
- Voice Agents consume **Real-time APIs** (Deepgram, OpenAI/Gemini, Murf).
- If you leave this "live" on your portfolio, anyone visiting can use it, which will **cost you money** (or eat up your free credits) very quickly.
- **Recommendation**:
  - **Option A (Safe)**: Deploy the Frontend on Vercel, but keep the Backend running **locally** only when you are demoing it. The link will load the UI, but it won't connect unless your local computer is running the agent.
  - **Option B (Demo Video)**: Record a high-quality video of the interaction (using the walkthrough we made) and embed that in your portfolio instead of a live interactive demo. This is safer and standard for expensive AI demos.
