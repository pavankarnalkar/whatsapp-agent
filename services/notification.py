"""Email and push notification sender."""

import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from config import settings


class NotificationService:
    """Handles email and push notifications for urgent messages."""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.notification_email = settings.notification_email
    
    async def send_email_notification(
        self, 
        subject: str, 
        message: str, 
        urgency_level: str = "Medium",
        sender_number: str = "Unknown"
    ) -> bool:
        """Send email notification for urgent messages."""
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.notification_email]):
            print("Email configuration incomplete. Skipping email notification.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.notification_email
            msg['Subject'] = f"[{urgency_level}] WhatsApp Message Alert"
            
            # Email body
            email_body = f"""
            New WhatsApp message received:
            
            From: {sender_number}
            Urgency Level: {urgency_level}
            Subject: {subject}
            
            Message:
            {message}
            
            ---
            WhatsApp AI Assistant
            """
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, self.notification_email, text)
            server.quit()
            
            print(f"Email notification sent successfully to {self.notification_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False
    
    async def send_urgent_alert(
        self, 
        message_data: Dict[str, Any],
        urgency_score: float
    ) -> bool:
        """Send urgent alert notification."""
        urgency_level = self._get_urgency_level(urgency_score)
        
        if urgency_score < 0.7:  # Only send notifications for high urgency
            return False
        
        subject = f"Urgent WhatsApp Message - {urgency_level}"
        message_text = message_data.get('message_text', 'No message content')
        sender_number = message_data.get('from_number', 'Unknown')
        
        return await self.send_email_notification(
            subject=subject,
            message=message_text,
            urgency_level=urgency_level,
            sender_number=sender_number
        )
    
    async def send_summary_notification(
        self, 
        phone_number: str, 
        summary: str, 
        stats: Dict[str, Any]
    ) -> bool:
        """Send conversation summary notification."""
        subject = f"Conversation Summary - {phone_number}"
        
        message = f"""
        Conversation Summary for {phone_number}:
        
        {summary}
        
        Statistics:
        - Total Messages: {stats.get('total_messages', 0)}
        - User Messages: {stats.get('user_messages', 0)}
        - Assistant Messages: {stats.get('assistant_messages', 0)}
        - Urgent Messages: {stats.get('urgent_messages', 0)}
        - Average Urgency: {stats.get('avg_urgency', 0):.2f}
        
        ---
        WhatsApp AI Assistant Daily Summary
        """
        
        return await self.send_email_notification(
            subject=subject,
            message=message,
            urgency_level="Low",
            sender_number=phone_number
        )
    
    def _get_urgency_level(self, urgency_score: float) -> str:
        """Convert urgency score to human-readable level."""
        if urgency_score >= 0.9:
            return "Critical"
        elif urgency_score >= 0.7:
            return "High"
        elif urgency_score >= 0.5:
            return "Medium"
        elif urgency_score >= 0.3:
            return "Low"
        else:
            return "Normal"
    
    async def test_notification_setup(self) -> bool:
        """Test notification setup by sending a test email."""
        return await self.send_email_notification(
            subject="Test Notification",
            message="This is a test notification from the WhatsApp AI Assistant.",
            urgency_level="Test",
            sender_number="System"
        )


# Global notification service instance
notification_service = NotificationService()