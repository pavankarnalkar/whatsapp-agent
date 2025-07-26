"""WhatsApp webhook logic for handling incoming messages."""

import json
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
from handlers.reply_logic import reply_logic
from config import settings


class WhatsAppWebhook:
    """Handles WhatsApp webhook events and message processing."""
    
    def __init__(self):
        self.verify_token = settings.whatsapp_webhook_verify_token
        self.access_token = settings.whatsapp_api_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> str:
        """Verify webhook subscription with WhatsApp."""
        if mode == "subscribe" and token == self.verify_token:
            print("Webhook verified successfully!")
            return challenge
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    
    async def process_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, str]:
        """Process incoming webhook event from WhatsApp."""
        try:
            # Extract message data from webhook
            message_data = self._extract_message_data(webhook_data)
            
            if not message_data:
                return {"status": "no_message_found"}
            
            print(f"Processing message from {message_data.get('from_number')}: {message_data.get('message_text')}")
            
            # Check if we should auto-reply
            should_reply = await reply_logic.should_auto_reply(message_data)
            
            if should_reply:
                # Generate response
                if reply_logic.is_business_hours():
                    response = await reply_logic.process_incoming_message(message_data)
                else:
                    response = await reply_logic.handle_out_of_hours_message(message_data)
                
                # Send response back to WhatsApp
                if response:
                    await self._send_message(message_data['from_number'], response)
                    return {"status": "replied", "response": response}
            else:
                # Just process and store the message without replying
                await reply_logic.process_incoming_message(message_data)
                return {"status": "processed"}
            
            return {"status": "success"}
            
        except Exception as e:
            print(f"Error processing webhook event: {e}")
            return {"status": "error", "error": str(e)}
    
    def _extract_message_data(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract message data from WhatsApp webhook payload."""
        try:
            entry = webhook_data.get('entry', [])
            if not entry:
                return None
            
            changes = entry[0].get('changes', [])
            if not changes:
                return None
            
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            # Extract basic message info
            message_data = {
                'message_id': message.get('id'),
                'from_number': message.get('from'),
                'to_number': value.get('metadata', {}).get('phone_number_id'),
                'timestamp': message.get('timestamp'),
                'message_type': message.get('type', 'text'),
                'is_from_user': True
            }
            
            # Extract message content based on type
            if message_data['message_type'] == 'text':
                message_data['message_text'] = message.get('text', {}).get('body', '')
            elif message_data['message_type'] == 'image':
                message_data['message_text'] = message.get('image', {}).get('caption', '[Image received]')
            elif message_data['message_type'] == 'document':
                message_data['message_text'] = f"[Document: {message.get('document', {}).get('filename', 'Unknown')}]"
            elif message_data['message_type'] == 'audio':
                message_data['message_text'] = '[Voice message received]'
            elif message_data['message_type'] == 'video':
                message_data['message_text'] = message.get('video', {}).get('caption', '[Video received]')
            else:
                message_data['message_text'] = f'[{message_data["message_type"]} message received]'
            
            return message_data
            
        except Exception as e:
            print(f"Error extracting message data: {e}")
            return None
    
    async def _send_message(self, to_number: str, message: str) -> bool:
        """Send message back to WhatsApp user."""
        if not all([self.access_token, self.phone_number_id]):
            print("WhatsApp API configuration incomplete. Cannot send message.")
            return False
        
        try:
            url = f"{self.api_base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    print(f"Message sent successfully to {to_number}")
                    return True
                else:
                    print(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    async def send_template_message(self, to_number: str, template_name: str, parameters: list = None) -> bool:
        """Send template message to WhatsApp user."""
        if not all([self.access_token, self.phone_number_id]):
            print("WhatsApp API configuration incomplete. Cannot send template message.")
            return False
        
        try:
            url = f"{self.api_base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en_US"
                    }
                }
            }
            
            if parameters:
                payload["template"]["components"] = [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": param} for param in parameters]
                    }
                ]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    print(f"Template message sent successfully to {to_number}")
                    return True
                else:
                    print(f"Failed to send template message. Status: {response.status_code}, Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error sending template message: {e}")
            return False


# Global webhook handler instance
whatsapp_webhook = WhatsAppWebhook()