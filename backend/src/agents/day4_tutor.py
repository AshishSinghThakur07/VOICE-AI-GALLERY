"""Day 4: Active Recall Tutor Agent with 3 learning modes."""
import logging
import json
from pathlib import Path
from typing import Literal

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

logger = logging.getLogger("agent.day4")

# Load tutor content
CONTENT_FILE = Path(__file__).parent.parent / "shared" / "data" / "day4_tutor_content.json"

def load_tutor_content():
    """Load tutor content from JSON file."""
    try:
        with open(CONTENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tutor content: {e}")
        return []

# Load content at module level
TUTOR_CONTENT = load_tutor_content()

# Mode-specific voices
MODE_VOICES = {
    "learn": "en-US-matthew",  # Matthew for learning
    "quiz": "en-US-alicia",    # Alicia for quizzing
    "teach_back": "en-US-ken", # Ken for teach-back
}


class TutorAgent(Agent):
    def __init__(self, mode: str = "learn") -> None:
        self.mode = mode
        instructions = self._get_instructions_for_mode(mode)
        super().__init__(instructions=instructions)

    def _get_instructions_for_mode(self, mode: str) -> str:
        """Get instructions based on current mode."""
        if mode == "learn":
            return """You are a friendly tutor in LEARN mode. Your job is to explain programming concepts clearly and engagingly.

            - Use the get_concept tool to retrieve concept information
            - Explain concepts in a clear, simple way
            - Use examples and analogies
            - Ask if the user wants to learn about another concept
            - If the user wants to switch modes, acknowledge it. Note: Mode switching requires starting a new session."""
        
        elif mode == "quiz":
            return """You are a friendly tutor in QUIZ mode. Your job is to test the user's understanding through questions.

            - Use the get_concept tool to get questions
            - Ask questions from the sample_question field
            - Provide feedback on answers
            - Be encouraging and helpful
            - If the user wants to switch modes, acknowledge it and let them know they can switch to learn or teach_back mode"""
        
        else:  # teach_back
            return """You are a friendly tutor in TEACH-BACK mode. Your job is to have the user explain concepts back to you.

            - Use the get_concept tool to get concept summaries
            - Ask the user to explain a concept in their own words
            - Listen carefully and provide qualitative feedback
            - Point out what they got right and what they might have missed
            - Be supportive and encouraging
            - If the user wants to switch modes, acknowledge it and let them know they can switch to learn or quiz mode"""

    @function_tool
    async def get_concept(self, context: RunContext, concept_id: str = None) -> str:
        """Get information about a programming concept.
        
        Args:
            concept_id: ID of the concept (e.g., "variables", "loops"). If None, returns list of available concepts.
            
        Returns:
            Concept information or list of available concepts
        """
        if not concept_id:
            concepts_list = [f"- {c['id']}: {c['title']}" for c in TUTOR_CONTENT]
            return "Available concepts:\n" + "\n".join(concepts_list)
        
        for concept in TUTOR_CONTENT:
            if concept["id"] == concept_id.lower():
                if self.mode == "learn":
                    return f"Concept: {concept['title']}\n\n{concept['summary']}"
                elif self.mode == "quiz":
                    return f"Question: {concept['sample_question']}"
                else:  # teach_back
                    return f"Please explain: {concept['title']}\n\nHere's a brief summary to help: {concept['summary']}"
        
        return f"Concept '{concept_id}' not found. Available concepts: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

    @function_tool
    async def list_concepts(self, context: RunContext) -> str:
        """List all available programming concepts to learn.
        
        Returns:
            List of available concepts
        """
        concepts = [f"{i+1}. {c['title']} ({c['id']})" for i, c in enumerate(TUTOR_CONTENT)]
        return "Available concepts:\n" + "\n".join(concepts)


# Global mode state (in production, use session state)
_current_mode = "learn"


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 4 tutor agent."""
    global _current_mode
    
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day4",
        "mode": _current_mode,
    }

    # Check if user wants to switch modes (simple implementation)
    # In a real scenario, you'd detect this from conversation or use agent handoffs
    
    # Set up voice AI pipeline with mode-specific voice
    voice = MODE_VOICES.get(_current_mode, "en-US-matthew")
    
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice=voice,
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
        agent=TutorAgent(mode=_current_mode),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

