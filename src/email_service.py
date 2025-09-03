#!/usr/bin/env python3
"""
Email service for KYC admin dashboard.
Handles sending emails to customers for status updates, requests, etc.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from typing import Optional, List
import json

class EmailService:
    """Service for sending emails to KYC customers."""
    
    def __init__(self):
        # Email configuration - you can move these to environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', 'kyc-admin@yourcompany.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.company_name = os.getenv('COMPANY_NAME', 'Your Company')
        
        # Email templates
        self.templates = {
            'status_update': {
                'subject': 'KYC Application Status Update',
                'template': """
Dear {customer_name},

Your KYC application (ID: {customer_id}) status has been updated.

**Current Status:** {status}
**Risk Level:** {risk_level}
**Updated On:** {update_date}

{additional_notes}

If you have any questions, please contact our support team.

Best regards,
{company_name} KYC Team
                """
            },
            'document_request': {
                'subject': 'Additional Documents Required',
                'template': """
Dear {customer_name},

We require additional documents to complete your KYC application (ID: {customer_id}).

**Required Documents:**
{required_documents}

**Reason:** {reason}

Please upload the requested documents through our customer portal.

If you have any questions, please contact our support team.

Best regards,
{company_name} KYC Team
                """
            },
            'approval': {
                'subject': 'KYC Application Approved',
                'template': """
Dear {customer_name},

Congratulations! Your KYC application (ID: {customer_id}) has been approved.

**Approval Details:**
- Status: Approved
- Risk Level: {risk_level}
- Approval Date: {approval_date}

{additional_notes}

You can now proceed with your account activities.

Best regards,
{company_name} KYC Team
                """
            },
            'rejection': {
                'subject': 'KYC Application Update',
                'template': """
Dear {customer_name},

We regret to inform you that your KYC application (ID: {customer_id}) requires attention.

**Current Status:** {status}
**Reason:** {reason}

{additional_notes}

Please review the feedback and resubmit your application if needed.

Best regards,
{company_name} KYC Team
                """
            },
            'custom': {
                'subject': 'KYC Application Update',
                'template': """
Dear {customer_name},

{message}

Best regards,
{company_name} KYC Team
                """
            }
        }
    
    def send_email(self, to_email: str, template_name: str, template_data: dict, 
                   custom_subject: Optional[str] = None, custom_message: Optional[str] = None) -> dict:
        """Send an email using a template."""
        try:
            if not self.sender_password:
                return {
                    "status": "error",
                    "message": "Email service not configured. Please set SMTP credentials."
                }
            
            # Get template
            if template_name not in self.templates:
                return {
                    "status": "error",
                    "message": f"Email template '{template_name}' not found"
                }
            
            template = self.templates[template_name]
            
            # Prepare email content
            if custom_subject:
                subject = custom_subject
            else:
                subject = template['subject']
            
            if custom_message:
                message = custom_message
            else:
                message = template['template'].format(
                    company_name=self.company_name,
                    **template_data
                )
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {to_email}",
                "email_details": {
                    "to": to_email,
                    "subject": subject,
                    "template": template_name,
                    "sent_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}"
            }
    
    def send_status_update_email(self, customer_email: str, customer_name: str, 
                                customer_id: str, status: str, risk_level: str, 
                                additional_notes: str = "") -> dict:
        """Send status update email."""
        template_data = {
            "customer_name": customer_name,
            "customer_id": customer_id,
            "status": status,
            "risk_level": risk_level,
            "update_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "additional_notes": additional_notes
        }
        return self.send_email(customer_email, "status_update", template_data)
    
    def send_document_request_email(self, customer_email: str, customer_name: str,
                                   customer_id: str, required_documents: List[str],
                                   reason: str) -> dict:
        """Send document request email."""
        template_data = {
            "customer_name": customer_name,
            "customer_id": customer_id,
            "required_documents": "\n".join([f"- {doc}" for doc in required_documents]),
            "reason": reason
        }
        return self.send_email(customer_email, "document_request", template_data)
    
    def send_approval_email(self, customer_email: str, customer_name: str,
                           customer_id: str, risk_level: str, additional_notes: str = "") -> dict:
        """Send approval email."""
        template_data = {
            "customer_name": customer_name,
            "customer_id": customer_id,
            "risk_level": risk_level,
            "approval_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "additional_notes": additional_notes
        }
        return self.send_email(customer_email, "approval", template_data)
    
    def send_rejection_email(self, customer_email: str, customer_name: str,
                            customer_id: str, status: str, reason: str, additional_notes: str = "") -> dict:
        """Send rejection/attention required email."""
        template_data = {
            "customer_name": customer_name,
            "customer_id": customer_id,
            "status": status,
            "reason": reason,
            "additional_notes": additional_notes
        }
        return self.send_email(customer_email, "rejection", template_data)
    
    def send_custom_email(self, customer_email: str, customer_name: str,
                         message: str, subject: str = "KYC Application Update") -> dict:
        """Send custom email."""
        template_data = {
            "customer_name": customer_name,
            "message": message
        }
        return self.send_email(customer_email, "custom", template_data, 
                              custom_subject=subject, custom_message=message)

# Global email service instance
email_service = EmailService() 