# WhatsApp Agent

A Flask-based webhook listener for receiving and logging WhatsApp messages via Twilio.

## Features

- Receives WhatsApp messages through Twilio webhook
- Parses sender, timestamp, and message content
- Stores messages in SQLite database
- Provides REST API to retrieve stored messages
- Health check endpoint for monitoring

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
python app.py
```

## API Endpoints

### POST /webhook/whatsapp
Webhook endpoint for receiving WhatsApp messages from Twilio.

**Expected Parameters:**
- `From`: Sender's WhatsApp number
- `To`: Recipient's WhatsApp number  
- `Body`: Message content
- `MessageSid`: Unique message identifier
- `ProfileName`: Sender's profile name

### GET /messages
Retrieve stored WhatsApp messages.

**Query Parameters:**
- `limit`: Number of messages to retrieve (default: 50)

### GET /health
Health check endpoint.

## Twilio Configuration

Configure your Twilio WhatsApp sandbox or number to send webhooks to:
```
https://your-domain.com/webhook/whatsapp
```

## Database Schema

Messages are stored in SQLite with the following fields:
- `id`: Auto-incrementing primary key
- `sender`: Sender's phone number
- `message_body`: Message content
- `timestamp`: Message timestamp
- `message_sid`: Twilio message ID
- `profile_name`: Sender's profile name
- `from_number`: Cleaned sender number
- `to_number`: Recipient number
- `created_at`: Database creation timestamp