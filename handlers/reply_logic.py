"""Automated response logic for WhatsApp messages."""

from typing import Dict, Any, Optional
from services.llm_client import llm_client
from services.urgency import urgency_detector
from services.notification import notification_service
from services.summarizer import summarizer
from store.db import db


class ReplyLogic:
    """Handles automated response generation and logic."""
    
    def __init__(self):
        self.auto_reply_enabled = True
        self.business_hours = (9, 17)  # 9 AM to 5 PM
        self.max_conversation_length = 100
    
    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Process incoming message and generate appropriate response."""
        message_text = message_data.get('message_text', '')
        from_number = message_data.get('from_number', '')
        
        if not message_text or not from_number:
            return None
        
        # Calculate urgency score
        urgency_score = urgency_detector.calculate_urgency_score(message_text)
        
        # Store message in database
        await db.store_message(
            message_id=message_data.get('message_id', ''),
            from_number=from_number,
            to_number=message_data.get('to_number', ''),
            message_text=message_text,
            urgency_score=urgency_score
        )
        
        # Send urgent notifications if needed
        if urgency_detector.should_notify(urgency_score):
            await notification_service.send_urgent_alert(message_data, urgency_score)
        
        # Get conversation history for context
        conversation_history = await db.get_conversation_history(from_number, limit=20)
        
        # Generate response
        response = await self._generate_contextual_response(
            message_text, 
            conversation_history, 
            urgency_score
        )
        
        # Store our response
        if response:
            await db.store_message(
                message_id=f"response_{message_data.get('message_id', '')}",
                from_number=message_data.get('to_number', ''),
                to_number=from_number,
                message_text=response,
                is_from_user=False
            )
        
        return response
    
    async def _generate_contextual_response(
        self, 
        message: str, 
        conversation_history: list,
        urgency_score: float
    ) -> str:
        """Generate contextual response based on message and history."""
        
        # Determine response type based on urgency
        if urgency_score >= 0.9:
            system_prompt = """You are a professional WhatsApp assistant handling a critical/urgent message. 
            Respond immediately with helpful information and let them know their message is being prioritized. 
            Keep responses concise but reassuring."""
        elif urgency_score >= 0.6:
            system_prompt = """You are a professional WhatsApp assistant handling an important message. 
            Provide helpful information and acknowledge the importance of their request. 
            Be professional and responsive."""
        else:
            system_prompt = """You are a friendly WhatsApp assistant. Provide helpful, 
            conversational responses. Be concise but personable."""
        
        # Check for common patterns
        message_lower = message.lower()
        
        # Greeting responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            base_response = await llm_client.generate_response(
                message, conversation_history, system_prompt
            )
            return base_response
        
        # FAQ responses
        if 'hours' in message_lower or 'open' in message_lower:
            return "Our business hours are Monday-Friday, 9 AM to 5 PM. How can I help you today?"
        
        if 'contact' in message_lower or 'phone' in message_lower or 'email' in message_lower:
            return "You can reach us through this WhatsApp number or email us at contact@company.com. What information do you need?"
        
        # Price/cost inquiries
        if any(word in message_lower for word in ['price', 'cost', 'how much', 'fee']):
            return await llm_client.generate_response(
                message + " (Please provide specific pricing information.)", 
                conversation_history, 
                system_prompt
            )
        
        # Support requests
        if any(word in message_lower for word in ['help', 'support', 'problem', 'issue', 'broken']):
            support_prompt = """You are a technical support assistant. Provide helpful troubleshooting steps 
            and ask clarifying questions to better understand the issue. Be empathetic and solution-focused."""
            return await llm_client.generate_response(message, conversation_history, support_prompt)
        
        # Default LLM response
        return await llm_client.generate_response(message, conversation_history, system_prompt)
    
    async def handle_out_of_hours_message(self, message_data: Dict[str, Any]) -> str:
        """Handle messages received outside business hours."""
        urgency_score = urgency_detector.calculate_urgency_score(
            message_data.get('message_text', '')
        )
        
        if urgency_score >= 0.8:
            # High urgency - immediate response
            await notification_service.send_urgent_alert(message_data, urgency_score)
            return ("Thank you for your urgent message. We've been notified and will respond as soon as possible. "
                   "For immediate assistance with emergencies, please call our emergency line.")
        else:
            # Normal message - standard out-of-hours response
            return ("Thank you for your message! We're currently outside business hours (9 AM - 5 PM, Mon-Fri). "
                   "We'll respond to your message during our next business day. For urgent matters, please call our emergency line.")
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        
        # Simple business hours check (9 AM to 5 PM, Monday-Friday)
        if now.weekday() >= 5:  # Weekend
            return False
        
        return self.business_hours[0] <= hour < self.business_hours[1]
    
    async def should_auto_reply(self, message_data: Dict[str, Any]) -> bool:
        """Determine if we should send an automatic reply."""
        if not self.auto_reply_enabled:
            return False
        
        # Don't reply to our own messages
        if not message_data.get('is_from_user', True):
            return False
        
        # Always reply to urgent messages
        urgency_score = urgency_detector.calculate_urgency_score(
            message_data.get('message_text', '')
        )
        if urgency_score >= 0.7:
            return True
        
        # Check conversation length to avoid spam
        from_number = message_data.get('from_number', '')
        conversation_history = await db.get_conversation_history(from_number, limit=5)
        
        from datetime import datetime
        recent_responses = [
            msg for msg in conversation_history 
            if not msg.get('is_from_user')
        ]
        
        # Limit to 3 auto-replies per hour
        if len(recent_responses) >= 3:
            return False
        
        return True


# Global reply logic instance
reply_logic = ReplyLogic()