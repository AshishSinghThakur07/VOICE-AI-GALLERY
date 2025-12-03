"""Day 2: Coffee Shop Barista Agent."""
import logging
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

logger = logging.getLogger("agent.day2")

# Order state structure
ORDER_SCHEMA = {
    "drinkType": "",
    "size": "",
    "milk": "",
    "extras": [],
    "name": "",
}


class BaristaAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly barista at a coffee shop. Your job is to help customers place their coffee orders.
            
            You should:
            - Greet customers warmly and ask what they'd like to order
            - Ask clarifying questions to fill in all order details:
              * What type of drink (coffee, latte, cappuccino, etc.)
              * What size (small, medium, large)
              * What type of milk (whole, skim, almond, oat, etc.)
              * Any extras (sugar, whipped cream, caramel, etc.)
              * Customer's name for the order
            - Once you have all the information, use the save_order tool to save the order
            - Be conversational and friendly throughout
            - Confirm the order details before saving
            
            Keep your responses concise and natural, as if you're having a real conversation.""",
        )

    @function_tool
    async def save_order(
        self,
        context: RunContext,
        drink_type: str,
        size: str,
        milk: str,
        extras: list[str],
        customer_name: str,
    ) -> str:
        """Save a completed coffee order to a JSON file.
        
        Args:
            drink_type: Type of drink (e.g., "latte", "cappuccino", "coffee")
            size: Size of the drink (e.g., "small", "medium", "large")
            milk: Type of milk (e.g., "whole", "skim", "almond", "oat")
            extras: List of extras (e.g., ["sugar", "whipped cream"])
            customer_name: Name of the customer
            
        Returns:
            Confirmation message
        """
        order = {
            "drinkType": drink_type,
            "size": size,
            "milk": milk,
            "extras": extras,
            "name": customer_name,
        }
        
        # Load existing orders
        orders = load_json("day2_orders.json", default=[])
        if not isinstance(orders, list):
            orders = []
        
        # Add new order
        orders.append(order)
        
        # Save to file
        if save_json("day2_orders.json", orders):
            logger.info(f"Order saved: {order}")
            return f"Order saved successfully! I've got your {size} {drink_type} with {milk} milk and {', '.join(extras) if extras else 'no extras'} ready for {customer_name}."
        else:
            return "I had trouble saving your order. Let me try again."

    @function_tool
    async def check_order_status(self, context: RunContext) -> str:
        """Check if the current order has all required fields filled.
        
        Returns:
            Status of the order fields
        """
        # This is a helper tool the agent can use to check what's missing
        return "Use this to check what order details are still needed."


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 2 barista agent."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day2",
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
        agent=BaristaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

