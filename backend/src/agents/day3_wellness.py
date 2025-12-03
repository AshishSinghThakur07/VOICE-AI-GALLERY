"""Day 3: Health & Wellness Voice Companion Agent."""
import logging
from datetime import datetime
from typing import Optional

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    MetricsCollectedEvent,
    RoomInputOptions,
    function_tool,
    metrics,
    tokenize,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from shared.tools.file_ops import save_json, load_json

logger = logging.getLogger("agent.day3")


class WellnessAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a supportive health and wellness companion. Your role is to conduct daily check-ins with users in a warm, empathetic, and grounded way.

            Your approach:
            - Ask about mood and energy levels naturally
            - Inquire about intentions/objectives for the day
            - Offer simple, realistic advice (non-medical, non-diagnostic)
            - Provide brief recaps of what was discussed
            - Reference past check-ins when relevant (use the get_wellness_history tool)
            
            Important guidelines:
            - Keep advice small, actionable, and grounded
            - Never diagnose or make medical claims
            - Be supportive but realistic
            - Keep conversations concise and focused
            - Always confirm understanding before ending
            
            When the user seems done, use the save_checkin tool to save the session.""",
        )

    @function_tool
    async def get_wellness_history(self, context: RunContext, days: int = 7) -> str:
        """Get wellness check-in history from the past N days.
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            Summary of past check-ins
        """
        try:
            history = load_json("day3_wellness_log.json", default=[])
            if not isinstance(history, list):
                return "No previous check-ins found."
            
            # Filter by date (simplified - just get recent entries)
            recent = history[-days:] if len(history) > days else history
            
            if not recent:
                return "This is your first check-in. Welcome!"
            
            # Build summary
            summary_parts = []
            for entry in recent[-3:]:  # Last 3 entries
                date = entry.get("date", "Unknown date")
                mood = entry.get("mood", "not recorded")
                summary_parts.append(f"On {date}, you reported feeling {mood}.")
            
            return " ".join(summary_parts) if summary_parts else "No recent check-ins."
        except Exception as e:
            logger.error(f"Error getting wellness history: {e}")
            return "I couldn't access your previous check-ins, but that's okay. Let's focus on today."

    @function_tool
    async def save_checkin(
        self,
        context: RunContext,
        mood: str,
        energy: str,
        objectives: list[str],
        summary: Optional[str] = None,
    ) -> str:
        """Save a wellness check-in to the log.
        
        Args:
            mood: How the user is feeling (e.g., "good", "tired", "anxious", "energetic")
            energy: Energy level (e.g., "high", "medium", "low")
            objectives: List of 1-3 things the user wants to accomplish today
            summary: Optional brief summary of the conversation
            
        Returns:
            Confirmation message
        """
        try:
            checkin = {
                "date": datetime.now().isoformat(),
                "mood": mood,
                "energy": energy,
                "objectives": objectives,
                "summary": summary or f"Check-in completed. Mood: {mood}, Energy: {energy}",
            }
            
            history = load_json("day3_wellness_log.json", default=[])
            if not isinstance(history, list):
                history = []
            
            history.append(checkin)
            
            if save_json("day3_wellness_log.json", history):
                logger.info(f"Wellness check-in saved: {checkin}")
                objectives_str = ", ".join(objectives) if objectives else "none specified"
                return f"Check-in saved! I've recorded that you're feeling {mood} with {energy} energy, and your objectives are: {objectives_str}. Take care today!"
            else:
                return "I had trouble saving your check-in, but I've noted everything we discussed."
        except Exception as e:
            logger.error(f"Error saving check-in: {e}")
            return "I noted everything we discussed. Have a great day!"


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 3 wellness companion."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day3",
    }

    # Set up voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=WellnessAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


