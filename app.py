from flask import Flask, request, jsonify
import logging
from datetime import datetime
from database import DatabaseManager
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db_manager = DatabaseManager()

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook endpoint to receive WhatsApp messages from Twilio.
    
    Expected Twilio webhook parameters:
    - From: sender's WhatsApp number (e.g., whatsapp:+1234567890)
    - To: recipient's WhatsApp number
    - Body: message content
    - MessageSid: unique message identifier
    - ProfileName: sender's profile name
    """
    try:
        # Parse webhook data from Twilio
        data = request.form
        
        # Extract message details
        sender = data.get('From', '')
        message_body = data.get('Body', '')
        message_sid = data.get('MessageSid', '')
        profile_name = data.get('ProfileName', '')
        to_number = data.get('To', '')
        
        # Clean up the sender number (remove 'whatsapp:' prefix if present)
        if sender.startswith('whatsapp:'):
            from_number = sender[9:]  # Remove 'whatsapp:' prefix
        else:
            from_number = sender
        
        # Use current timestamp if not provided by Twilio
        timestamp = datetime.now().isoformat()
        
        # Log the received message
        logger.info(f"Received WhatsApp message from {from_number}: {message_body}")
        
        # Store message in database
        message_id = db_manager.log_message(
            sender=from_number,
            message_body=message_body,
            timestamp=timestamp,
            message_sid=message_sid,
            profile_name=profile_name,
            from_number=from_number,
            to_number=to_number
        )
        
        logger.info(f"Message stored with ID: {message_id}")
        
        # Return success response to Twilio
        return jsonify({
            'status': 'success',
            'message_id': message_id,
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to process webhook'
        }), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    """
    Endpoint to retrieve stored WhatsApp messages.
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        messages = db_manager.get_messages(limit=limit)
        
        # Convert to list of dictionaries for JSON response
        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg[0],
                'sender': msg[1],
                'message_body': msg[2],
                'timestamp': msg[3],
                'message_sid': msg[4],
                'profile_name': msg[5],
                'from_number': msg[6],
                'to_number': msg[7],
                'created_at': msg[8]
            })
        
        return jsonify({
            'status': 'success',
            'messages': message_list,
            'count': len(message_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving messages: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve messages'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'WhatsApp Webhook Listener',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    logger.info("Starting WhatsApp webhook listener...")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )