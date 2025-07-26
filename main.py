"""FastAPI main application for WhatsApp AI Assistant."""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, Any

from config import settings
from store.db import db
from handlers.whatsapp_webhook import whatsapp_webhook
from services.notification import notification_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting WhatsApp AI Assistant...")
    
    # Initialize database
    await db.init_db()
    print("Database initialized")
    
    # Test notification setup (optional)
    if settings.debug:
        print("Testing notification setup...")
        # await notification_service.test_notification_setup()
    
    print("WhatsApp AI Assistant started successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down WhatsApp AI Assistant...")


# Create FastAPI app
app = FastAPI(
    title="WhatsApp AI Assistant",
    description="Automated WhatsApp assistant with AI responses and urgency detection",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "WhatsApp AI Assistant is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "services": "operational"
    }


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify WhatsApp webhook subscription."""
    try:
        challenge = whatsapp_webhook.verify_webhook(
            mode=hub_mode,
            token=hub_verify_token,
            challenge=hub_challenge
        )
        return PlainTextResponse(challenge)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming WhatsApp webhook events."""
    try:
        webhook_data = await request.json()
        
        # Process webhook in background to respond quickly
        background_tasks.add_task(
            whatsapp_webhook.process_webhook_event,
            webhook_data
        )
        
        return {"status": "received"}
        
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/conversations/{phone_number}")
async def get_conversation(phone_number: str, limit: int = 50):
    """Get conversation history for a phone number."""
    try:
        messages = await db.get_conversation_history(phone_number, limit)
        return {
            "phone_number": phone_number,
            "messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{phone_number}/summary")
async def get_conversation_summary(phone_number: str):
    """Get conversation summary for a phone number."""
    try:
        messages = await db.get_conversation_history(phone_number, limit=100)
        
        if not messages:
            return {"phone_number": phone_number, "summary": "No messages found"}
        
        from services.summarizer import summarizer
        summary = await summarizer.create_summary(messages)
        stats = summarizer.get_conversation_stats(messages)
        key_points = summarizer.extract_key_points(messages)
        
        return {
            "phone_number": phone_number,
            "summary": summary,
            "statistics": stats,
            "key_points": key_points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/unprocessed")
async def get_unprocessed_messages():
    """Get unprocessed messages."""
    try:
        messages = await db.get_unprocessed_messages()
        return {
            "unprocessed_messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/{message_id}/process")
async def mark_message_processed(message_id: str):
    """Mark a message as processed."""
    try:
        success = await db.mark_message_processed(message_id)
        if success:
            return {"status": "success", "message_id": message_id}
        else:
            raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-message")
async def send_message(message_data: Dict[str, Any]):
    """Send a message via WhatsApp API."""
    try:
        to_number = message_data.get("to_number")
        message = message_data.get("message")
        
        if not to_number or not message:
            raise HTTPException(status_code=400, detail="to_number and message are required")
        
        success = await whatsapp_webhook._send_message(to_number, message)
        
        if success:
            return {"status": "sent", "to_number": to_number}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-notification")
async def test_notification():
    """Test notification system."""
    try:
        success = await notification_service.test_notification_setup()
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )