"""OpenAI LLM client wrapper."""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from config import settings


class LLMClient:
    """Wrapper for OpenAI API and local model interactions."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]] = None,
        system_prompt: str = None
    ) -> str:
        """Generate a response using the LLM."""
        try:
            if not self.client:
                return "OpenAI API key not configured. Please check your settings."
            
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system", 
                    "content": "You are a helpful WhatsApp assistant. Respond concisely and helpfully."
                })
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = "user" if msg.get("is_from_user") else "assistant"
                    if msg.get("message_text"):
                        messages.append({
                            "role": role,
                            "content": msg["message_text"]
                        })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return "I'm sorry, I'm having trouble processing your message right now. Please try again later."
    
    async def summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a summary of the conversation."""
        try:
            if not self.client:
                return "OpenAI API key not configured."
            
            if not messages:
                return "No messages to summarize."
            
            # Prepare conversation text
            conversation_text = ""
            for msg in messages:
                role = "User" if msg.get("is_from_user") else "Assistant"
                conversation_text += f"{role}: {msg.get('message_text', '')}\n"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following WhatsApp conversation in 2-3 sentences. Focus on key topics and any action items."
                    },
                    {
                        "role": "user",
                        "content": conversation_text
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error summarizing conversation: {e}")
            return "Unable to generate summary at this time."
    
    async def detect_urgency(self, message: str) -> float:
        """Detect urgency level in a message (0.0 to 1.0)."""
        try:
            if not self.client:
                # Fallback to keyword-based detection
                return self._keyword_urgency_detection(message)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the urgency level of the following message on a scale of 0.0 to 1.0.
                        
                        0.0 = No urgency (casual conversation, general questions)
                        0.3 = Low urgency (routine business, follow-ups)
                        0.6 = Medium urgency (time-sensitive but not critical)
                        0.9 = High urgency (critical issues, emergencies)
                        1.0 = Maximum urgency (life-threatening, emergency situations)
                        
                        Respond with only the numerical score (e.g., 0.7)."""
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            urgency_str = response.choices[0].message.content.strip()
            return min(max(float(urgency_str), 0.0), 1.0)
            
        except Exception as e:
            print(f"Error detecting urgency: {e}")
            return self._keyword_urgency_detection(message)
    
    def _keyword_urgency_detection(self, message: str) -> float:
        """Fallback keyword-based urgency detection."""
        message_lower = message.lower()
        urgency_keywords = settings.urgency_keywords
        
        for keyword in urgency_keywords:
            if keyword.lower() in message_lower:
                return 0.8
        
        return 0.1


# Global LLM client instance
llm_client = LLMClient()