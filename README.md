# WhatsApp AI Assistant MVP

A professional WhatsApp assistant with AI-powered responses, urgency detection, and automated notifications.

## Features

- **Automated WhatsApp Responses**: AI-powered responses using OpenAI GPT models
- **Urgency Detection**: Automatically detects urgent messages and sends notifications
- **Conversation Summarization**: Generates summaries of long conversations
- **Message Storage**: SQLite database for storing and retrieving conversation history
- **Email Notifications**: Sends email alerts for urgent messages
- **Business Hours Support**: Different responses for business hours vs. after hours
- **Webhook Integration**: Full WhatsApp Business API webhook support

## Project Structure

```
/whatsapp-ai-assistant-mvp
├── main.py                 # FastAPI main application
├── handlers/
│   ├── whatsapp_webhook.py # WhatsApp webhook logic
│   └── reply_logic.py      # Automated response logic
├── services/
│   ├── llm_client.py       # OpenAI / local model wrapper
│   ├── notification.py     # Email/Push notification sender
│   ├── summarizer.py       # Chat summarization logic
│   └── urgency.py          # Urgency detection logic
├── store/
│   └── db.py               # SQLite wrapper for message storage
├── config.py               # Environment variables + settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (template)
└── README.md               # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd whatsapp-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env .env.local
# Edit .env.local with your actual configuration
```

4. Initialize the database:
```bash
python -c "import asyncio; from store.db import db; asyncio.run(db.init_db())"
```

## Configuration

Update the `.env` file with your actual credentials:

### WhatsApp Business API
- `WHATSAPP_API_TOKEN`: Your WhatsApp Business API access token
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN`: Webhook verification token
- `WHATSAPP_PHONE_NUMBER_ID`: Your WhatsApp Business phone number ID

### OpenAI API
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-3.5-turbo)

### Email Notifications
- `SMTP_SERVER`: SMTP server for sending emails
- `SMTP_USERNAME`: Email username
- `SMTP_PASSWORD`: Email password or app password
- `NOTIFICATION_EMAIL`: Email address to receive notifications

## Usage

### Start the Application

```bash
python main.py
```

The application will start on `http://localhost:8000`

### API Endpoints

- `GET /`: Health check
- `GET /webhook`: WhatsApp webhook verification
- `POST /webhook`: WhatsApp webhook handler
- `GET /conversations/{phone_number}`: Get conversation history
- `GET /conversations/{phone_number}/summary`: Get conversation summary
- `GET /messages/unprocessed`: Get unprocessed messages
- `POST /send-message`: Send a message via WhatsApp API

### WhatsApp Webhook Setup

1. Configure your WhatsApp Business API webhook URL to point to: `https://your-domain.com/webhook`
2. Use the `WHATSAPP_WEBHOOK_VERIFY_TOKEN` for webhook verification
3. The application will automatically process incoming messages and send AI-generated responses

## Features in Detail

### Automated Responses
- Context-aware responses using conversation history
- Different response styles based on message urgency
- Business hours vs. after-hours responses
- FAQ handling for common questions

### Urgency Detection
- Keyword-based urgency scoring (0.0 to 1.0)
- Pattern matching for urgent language
- Automatic notifications for high-urgency messages
- Configurable urgency thresholds

### Conversation Management
- Automatic conversation summarization
- Message history storage and retrieval
- Conversation statistics and analytics
- Key point extraction

### Notifications
- Email alerts for urgent messages
- Daily conversation summaries
- Configurable notification thresholds
- Test notification functionality

## Development

### Running in Development Mode

```bash
# Set DEBUG=true in .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

Test the notification system:
```bash
curl -X POST http://localhost:8000/test-notification
```

Test message sending:
```bash
curl -X POST http://localhost:8000/send-message \
  -H "Content-Type: application/json" \
  -d '{"to_number": "1234567890", "message": "Test message"}'
```

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use environment-specific configuration files
- Regularly rotate API keys and access tokens
- Implement proper webhook security in production

## License

This project is licensed under the MIT License.