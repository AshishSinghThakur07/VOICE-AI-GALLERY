"""Day 9: E-commerce Agent (ACP-inspired)."""
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

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

logger = logging.getLogger("agent.day9")

# Load catalog
CATALOG_FILE = Path(__file__).parent.parent / "shared" / "data" / "day9_catalog.json"

def load_catalog():
    """Load product catalog from JSON file."""
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return {"products": []}

CATALOG = load_catalog()


class EcommerceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful e-commerce shopping assistant. Your role is to help customers browse products and place orders.

            Your approach:
            - Greet customers warmly
            - Help them explore the product catalog using the list_products tool
            - Answer questions about products (price, color, size, availability)
            - When customer wants to buy something, use the create_order tool
            - Be helpful and conversational
            - When asked "what did I just buy?" or "show my last order", use the get_last_order tool
            
            Product categories available:
            - Mugs (coffee mugs in various colors)
            - T-shirts (cotton t-shirts)
            - Hoodies (warm hoodies)
            - Notebooks (leather and spiral notebooks)
            
            Keep responses concise and helpful. Focus on helping customers find what they need.""",
        )

    @function_tool
    async def list_products(
        self,
        context: RunContext,
        category: Optional[str] = None,
        max_price: Optional[int] = None,
        color: Optional[str] = None,
    ) -> str:
        """List products from the catalog with optional filters.
        
        Args:
            category: Filter by category (mug, tshirt, hoodie, notebook)
            max_price: Maximum price filter
            color: Filter by color
            
        Returns:
            List of matching products with details
        """
        products = CATALOG.get("products", [])
        filtered = []
        
        for product in products:
            # Apply filters
            if category and product.get("category") != category:
                continue
            if max_price and product.get("price", 0) > max_price:
                continue
            if color and product.get("color", "").lower() != color.lower():
                continue
            
            filtered.append(product)
        
        if not filtered:
            return f"No products found matching your criteria. Try browsing by category: mug, tshirt, hoodie, or notebook."
        
        # Format results
        formatted = []
        for i, product in enumerate(filtered[:10], 1):  # Limit to 10 results
            price = product.get("price", 0)
            currency = product.get("currency", "INR")
            color = product.get("color", "")
            size = product.get("size", "")
            
            details = f"{i}. {product['name']} - ₹{price} {currency}"
            if color:
                details += f" (Color: {color})"
            if size:
                details += f" (Size: {size})"
            details += f" - {product.get('description', '')}"
            details += f" [ID: {product['id']}]"
            
            formatted.append(details)
        
        return "Found products:\n" + "\n".join(formatted)

    @function_tool
    async def create_order(
        self,
        context: RunContext,
        line_items: List[Dict[str, any]],
    ) -> str:
        """Create an order with line items (ACP-inspired structure).
        
        Args:
            line_items: List of items to order, each with product_id and quantity
            Example: [{"product_id": "mug-001", "quantity": 2}]
            
        Returns:
            Order confirmation with order ID
        """
        try:
            # Validate and process line items
            order_items = []
            total = 0
            currency = "INR"
            
            for item in line_items:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)
                
                # Find product in catalog
                product = None
                for p in CATALOG.get("products", []):
                    if p["id"] == product_id:
                        product = p
                        break
                
                if not product:
                    return f"Product with ID '{product_id}' not found in catalog."
                
                unit_amount = product.get("price", 0)
                item_total = unit_amount * quantity
                total += item_total
                
                order_items.append({
                    "product_id": product_id,
                    "name": product.get("name"),
                    "quantity": quantity,
                    "unit_amount": unit_amount,
                    "currency": currency,
                })
            
            # Create order object (ACP-inspired)
            order = {
                "id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "line_items": order_items,
                "total": total,
                "currency": currency,
                "created_at": datetime.now().isoformat(),
                "status": "PENDING",
            }
            
            # Save order
            orders = load_json("day9_orders.json", default=[])
            if not isinstance(orders, list):
                orders = []
            orders.append(order)
            
            if save_json("day9_orders.json", orders):
                logger.info(f"Order created: {order['id']}")
                
                # Format confirmation
                items_summary = []
                for item in order_items:
                    items_summary.append(f"{item['quantity']}x {item['name']} (₹{item['unit_amount']} each)")
                
                confirmation = f"Order placed successfully!\n\nOrder ID: {order['id']}\n"
                confirmation += f"Items:\n" + "\n".join(f"  - {item}" for item in items_summary)
                confirmation += f"\n\nTotal: ₹{total} {currency}\nStatus: {order['status']}"
                
                return confirmation
            else:
                return "I had trouble creating your order. Please try again."
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return f"Error creating order: {str(e)}"

    @function_tool
    async def get_last_order(self, context: RunContext) -> str:
        """Get the most recent order.
        
        Returns:
            Last order summary
        """
        orders = load_json("day9_orders.json", default=[])
        if not isinstance(orders, list) or not orders:
            return "You haven't placed any orders yet."
        
        order = orders[-1]  # Most recent order
        
        items_summary = []
        for item in order.get("line_items", []):
            items_summary.append(f"{item['quantity']}x {item['name']} - ₹{item['unit_amount'] * item['quantity']}")
        
        summary = f"Your last order:\n\nOrder ID: {order['id']}\n"
        summary += f"Items:\n" + "\n".join(f"  - {item}" for item in items_summary)
        summary += f"\n\nTotal: ₹{order['total']} {order.get('currency', 'INR')}\n"
        summary += f"Status: {order.get('status', 'PENDING')}\n"
        summary += f"Date: {order.get('created_at', 'Unknown')}"
        
        return summary


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 9 e-commerce agent."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day9",
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
        agent=EcommerceAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


