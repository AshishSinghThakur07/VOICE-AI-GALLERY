# Project Report: Voice Agent Challenge

## 1. Project Overview
This project is a comprehensive exploration of building **Real-time Voice AI Agents**. Over the course of 10 days, we built various agents ranging from simple conversationalists to complex game masters and improv hosts.

## 2. Technology Stack
The project uses a modern, industry-standard stack for building real-time AI applications:

### Frontend
- **Next.js (React)**: Framework for the web interface.
- **LiveKit Client SDK**: Handles real-time WebRTC audio/video connections.
- **Tailwind CSS & Framer Motion**: For styling and smooth animations.

### Backend
- **Python**: Core language for the agent logic.
- **LiveKit Agents Framework**: The backbone that connects the AI models to the real-time room.
- **Docker**: For containerizing the application for deployment.

### AI Models & APIs
- **STT (Speech-to-Text)**: **Deepgram Nova-3** (Fast, accurate transcription).
- **LLM (Language Model)**: **Google Gemini 2.5 Flash** (Low latency, high intelligence).
- **TTS (Text-to-Speech)**: **Murf Falcon** (The star of the show - ultra-low latency, high-quality human-like voices).

## 3. Key Learnings
- **Real-time Latency**: The biggest challenge in voice AI is latency. Using fast models like Murf Falcon and Gemini Flash is critical to make the conversation feel natural.
- **State Management**: Managing the state of a conversation (e.g., game rounds, inventory, user intent) requires careful design in the backend agent.
- **Tool Calling**: We learned how to give the AI "tools" (functions) to interact with the world, like saving game state or looking up information.
- **Event-Driven Architecture**: The agents react to events (user started speaking, user stopped speaking), which is different from traditional request-response web apps.

## 4. Agents Implemented
You can test these agents locally by visiting the following URLs:

- **Day 1 (Basic)**: `http://localhost:3000/day/1`
- **Day 2 (Barista)**: `http://localhost:3000/day/2`
- **Day 3 (Wellness)**: `http://localhost:3000/day/3`
- **Day 4 (Tutor)**: `http://localhost:3000/day/4`
- **Day 5 (SDR)**: `http://localhost:3000/day/5`
- **Day 6 (Fraud)**: `http://localhost:3000/day/6`
- **Day 7 (Food)**: `http://localhost:3000/day/7`
- **Day 8 (Game Master)**: `http://localhost:3000/day/8`
- **Day 9 (E-commerce)**: `http://localhost:3000/day/9`
- **Day 10 (Improv Battle)**: `http://localhost:3000/day10` (Special UI) or `http://localhost:3000/day/10`

## 5. Conclusion
This project demonstrates the power of combining real-time communication (LiveKit) with generative AI. The result is a new class of applications where users can talk naturally to computers.
