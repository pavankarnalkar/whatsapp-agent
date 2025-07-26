#!/usr/bin/env python3
"""
Simple test script for the WhatsApp webhook listener.
Tests the database functionality and webhook endpoints.
"""

import os
import sys
import sqlite3
import requests
import time
import json
from datetime import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

def test_database():
    """Test database functionality."""
    print("Testing database functionality...")
    
    # Use a test database
    test_db_path = "test_whatsapp_messages.db"
    db_manager = DatabaseManager(test_db_path)
    
    # Test logging a message
    message_id = db_manager.log_message(
        sender="+1234567890",
        message_body="Test message from unit test",
        timestamp=datetime.now().isoformat(),
        message_sid="TEST123",
        profile_name="Test User",
        from_number="+1234567890",
        to_number="+0987654321"
    )
    
    print(f"✓ Message logged with ID: {message_id}")
    
    # Test retrieving messages
    messages = db_manager.get_messages(limit=10)
    assert len(messages) >= 1, "No messages retrieved from database"
    print(f"✓ Retrieved {len(messages)} messages")
    
    # Clean up test database
    os.remove(test_db_path)
    print("✓ Database test completed")

def test_webhook_endpoints():
    """Test webhook endpoints (requires Flask app to be running)."""
    print("\nTesting webhook endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        health_data = response.json()
        assert health_data["status"] == "healthy", "Health check status not healthy"
        print("✓ Health endpoint working")
        
        # Test messages endpoint (initial state)
        response = requests.get(f"{base_url}/messages", timeout=5)
        assert response.status_code == 200, f"Messages endpoint failed: {response.status_code}"
        messages_data = response.json()
        assert "messages" in messages_data, "Messages data missing 'messages' key"
        print("✓ Messages endpoint working")
        
        # Test webhook endpoint
        webhook_data = {
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+0987654321",
            "Body": "Test webhook message",
            "MessageSid": "TEST_WEBHOOK_123",
            "ProfileName": "Test Webhook User"
        }
        
        response = requests.post(
            f"{base_url}/webhook/whatsapp",
            data=webhook_data,
            timeout=5
        )
        assert response.status_code == 200, f"Webhook failed: {response.status_code}"
        webhook_response = response.json()
        assert webhook_response["status"] == "success", "Webhook response status not success"
        print("✓ Webhook endpoint working")
        
        # Verify message was stored
        response = requests.get(f"{base_url}/messages?limit=1", timeout=5)
        messages_data = response.json()
        assert len(messages_data["messages"]) >= 1, "Message not stored properly"
        latest_message = messages_data["messages"][0]
        assert latest_message["message_body"] == "Test webhook message", "Message body not stored correctly"
        print("✓ Message storage verified")
        
        print("✓ All webhook endpoint tests passed")
        
    except requests.ConnectionError:
        print("⚠ Flask app not running. Start with 'python app.py' to test endpoints")
        return False
    except Exception as e:
        print(f"✗ Webhook test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("WhatsApp Webhook Listener Test Suite")
    print("=" * 40)
    
    # Test database functionality
    test_database()
    
    # Test webhook endpoints
    test_webhook_endpoints()
    
    print("\n" + "=" * 40)
    print("All tests completed!")