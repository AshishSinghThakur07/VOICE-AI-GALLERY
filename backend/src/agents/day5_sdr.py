"""Day 5: Sales Development Representative (SDR) Agent."""
import logging
import json
from pathlib import Path
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
from pathlib import Path as PathLib

# Add src directory to path for imports
src_path = PathLib(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from shared.tools.file_ops import save_json, load_json

logger = logging.getLogger("agent.day5")

# Load company FAQ
FAQ_FILE = Path(__file__).parent.parent / "shared" / "data" / "day5_company_faq.json"

def load_faq():
    """Load company FAQ from JSON file."""
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading FAQ: {e}")
        return {"company_name": "TechFlow Solutions", "faq": []}

COMPANY_DATA = load_faq()


class SDRAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"""You are a Sales Development Representative (SDR) for {COMPANY_DATA.get('company_name', 'TechFlow Solutions')}, an Indian startup.

            Your role:
            - Greet visitors warmly and professionally
            - Ask what brought them here and what they're working on
            - Answer questions about the company and product using the FAQ (use search_faq tool)
            - Understand the visitor's needs and use case
            - Collect lead information naturally during conversation:
              * Name
              * Company
              * Email
              * Role
              * Use case (what they want to use this for)
              * Team size
              * Timeline (now / soon / later)
            - Keep the conversation focused and helpful
            - When the user seems done (says "that's all", "thanks", "I'm done"), use the save_lead tool to save their information
            - Provide a brief verbal summary before ending
            
            Be friendly, professional, and genuinely interested in helping the visitor.""",
        )

    @function_tool
    async def search_faq(self, context: RunContext, query: str) -> str:
        """Search the company FAQ for answers to questions.
        
        Args:
            query: The question or topic to search for
            
        Returns:
            Relevant FAQ answer or information
        """
        query_lower = query.lower()
        faq_list = COMPANY_DATA.get("faq", [])
        
        # Simple keyword matching
        for item in faq_list:
            question = item.get("question", "").lower()
            answer = item.get("answer", "")
            
            # Check if query matches question keywords
            if any(word in question for word in query_lower.split() if len(word) > 3):
                return f"{item['question']}\n\n{answer}"
        
        # If no match, return general info
        company_name = COMPANY_DATA.get("company_name", "TechFlow Solutions")
        description = COMPANY_DATA.get("description", "An AI-powered workflow automation platform.")
        
        return f"I don't have a specific answer for that, but {company_name} is {description}. Would you like to know more about our pricing, features, or how it works?"

    @function_tool
    async def save_lead(
        self,
        context: RunContext,
        name: str,
        company: str,
        email: str,
        role: str,
        use_case: str,
        team_size: str,
        timeline: str,
    ) -> str:
        """Save a lead's information to the leads database.
        
        Args:
            name: Lead's name
            company: Company name
            email: Email address
            role: Job role/title
            use_case: What they want to use the product for
            team_size: Size of their team
            timeline: When they're looking to implement (now/soon/later)
            
        Returns:
            Confirmation message with summary
        """
        try:
            lead = {
                "name": name,
                "company": company,
                "email": email,
                "role": role,
                "use_case": use_case,
                "team_size": team_size,
                "timeline": timeline,
                "date": datetime.now().isoformat(),
            }
            
            leads = load_json("day5_leads.json", default=[])
            if not isinstance(leads, list):
                leads = []
            
            leads.append(lead)
            
            if save_json("day5_leads.json", leads):
                logger.info(f"Lead saved: {lead}")
                summary = f"Great! I've saved your information. Here's a quick summary: {name} from {company} ({role}) is interested in using our platform for {use_case} with a team of {team_size}, looking to implement {timeline}. We'll be in touch soon at {email}!"
                return summary
            else:
                return "I've noted your information. Thank you for your interest!"
        except Exception as e:
            logger.error(f"Error saving lead: {e}")
            return "Thank you for your interest! We'll be in touch soon."


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 5 SDR agent."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day5",
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
        agent=SDRAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


