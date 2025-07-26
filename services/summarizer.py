"""Chat summarization logic."""

from typing import List, Dict, Any
from services.llm_client import llm_client


class ConversationSummarizer:
    """Handles conversation summarization logic."""
    
    def __init__(self):
        self.max_messages_for_summary = 50
        self.min_messages_for_summary = 5
    
    async def should_summarize(self, messages: List[Dict[str, Any]]) -> bool:
        """Determine if a conversation should be summarized."""
        if len(messages) < self.min_messages_for_summary:
            return False
        
        # Summarize if we have enough messages
        if len(messages) >= self.max_messages_for_summary:
            return True
        
        # Summarize if the conversation spans multiple days
        if len(messages) >= 20:
            return True
        
        return False
    
    async def create_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Create a summary of the conversation."""
        if not messages:
            return "No messages to summarize."
        
        # Use the LLM client to generate summary
        summary = await llm_client.summarize_conversation(messages)
        return summary
    
    def extract_key_points(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from conversation for quick reference."""
        key_points = []
        
        # Look for messages with high urgency
        urgent_messages = [
            msg for msg in messages 
            if msg.get('urgency_score', 0) > 0.7
        ]
        
        for msg in urgent_messages:
            key_points.append(f"Urgent: {msg.get('message_text', '')[:100]}...")
        
        # Look for questions (messages ending with ?)
        questions = [
            msg for msg in messages 
            if msg.get('message_text', '').strip().endswith('?')
        ]
        
        for msg in questions[-3:]:  # Last 3 questions
            key_points.append(f"Question: {msg.get('message_text', '')}")
        
        return key_points[:5]  # Return top 5 key points
    
    def get_conversation_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the conversation."""
        if not messages:
            return {}
        
        user_messages = [msg for msg in messages if msg.get('is_from_user')]
        assistant_messages = [msg for msg in messages if not msg.get('is_from_user')]
        
        urgent_messages = [
            msg for msg in messages 
            if msg.get('urgency_score', 0) > 0.7
        ]
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'urgent_messages': len(urgent_messages),
            'avg_urgency': sum(msg.get('urgency_score', 0) for msg in messages) / len(messages),
            'first_message_time': messages[-1].get('timestamp') if messages else None,
            'last_message_time': messages[0].get('timestamp') if messages else None,
        }


# Global summarizer instance
summarizer = ConversationSummarizer()