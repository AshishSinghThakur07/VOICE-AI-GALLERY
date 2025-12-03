"""Day 6: Fraud Alert Voice Agent."""
import logging
import json
from pathlib import Path
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
from pathlib import Path as PathLib

# Add src directory to path for imports
src_path = PathLib(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from shared.tools.file_ops import save_json, load_json

logger = logging.getLogger("agent.day6")

# Load fraud cases
FRAUD_CASES_FILE = Path(__file__).parent.parent / "shared" / "data" / "day6_fraud_cases.json"

def load_fraud_cases():
    """Load fraud cases from JSON file."""
    try:
        with open(FRAUD_CASES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading fraud cases: {e}")
        return []

def save_fraud_cases(cases):
    """Save fraud cases to JSON file."""
    try:
        with open(FRAUD_CASES_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving fraud cases: {e}")
        return False


class FraudAlertAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a fraud detection representative for a bank's security department. Your role is to contact customers about suspicious transactions and verify if they are legitimate.

            Your approach:
            - Introduce yourself clearly as a bank fraud department representative
            - Explain that you're calling about a suspicious transaction
            - Ask for the customer's username to look up their case
            - Once you have the username, use the get_fraud_case tool to retrieve transaction details
            - Ask a security question to verify the customer's identity (use the security question from the case)
            - If verification passes, read out the suspicious transaction details
            - Ask if the customer made this transaction (yes/no)
            - Based on their answer:
              * If YES: Use update_fraud_case to mark as "confirmed_safe"
              * If NO: Use update_fraud_case to mark as "confirmed_fraud"
            - If verification fails, politely end the call and mark as "verification_failed"
            
            Important:
            - Be calm, professional, and reassuring
            - Never ask for full card numbers, PINs, or passwords
            - Only use non-sensitive information for verification
            - Clearly explain what action will be taken (card blocked, dispute raised, etc.) if fraud is confirmed""",
        )

    @function_tool
    async def get_fraud_case(self, context: RunContext, username: str) -> str:
        """Get fraud case details for a username.
        
        Args:
            username: Customer's username
            
        Returns:
            Fraud case details or error message
        """
        cases = load_fraud_cases()
        
        # Find case by username
        for case in cases:
            if case.get("userName", "").lower() == username.lower():
                if case.get("case") == "pending_review":
                    return json.dumps(case, indent=2)
                else:
                    return f"Case for {username} has already been processed. Status: {case.get('case')}"
        
        return f"No pending fraud case found for username: {username}"

    @function_tool
    async def update_fraud_case(
        self,
        context: RunContext,
        username: str,
        status: str,
        outcome_note: str,
    ) -> str:
        """Update a fraud case with the outcome.
        
        Args:
            username: Customer's username
            status: New status (confirmed_safe, confirmed_fraud, verification_failed)
            outcome_note: Note about the outcome
            
        Returns:
            Confirmation message
        """
        cases = load_fraud_cases()
        
        # Find and update case
        for case in cases:
            if case.get("userName", "").lower() == username.lower():
                case["case"] = status
                case["outcome"] = status
                case["outcomeNote"] = outcome_note
                
                if save_fraud_cases(cases):
                    logger.info(f"Fraud case updated: {username} -> {status}")
                    
                    if status == "confirmed_safe":
                        return f"Transaction confirmed as legitimate. The case has been closed. Thank you for verifying."
                    elif status == "confirmed_fraud":
                        return f"Fraud confirmed. I've blocked the card ending in {case.get('cardEnding', '****')} and initiated a dispute. A new card will be issued within 5-7 business days. Thank you for reporting this."
                    else:
                        return f"Verification failed. For security reasons, I cannot proceed. Please contact our customer service directly. Thank you."
                else:
                    return "I had trouble updating the case, but I've noted the outcome."
        
        return f"Case not found for username: {username}"


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 6 fraud alert agent."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day6",
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
        agent=FraudAlertAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


