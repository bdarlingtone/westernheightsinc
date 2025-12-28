#!/usr/bin/env python3
"""
Western Heights Inc. - Contact Form Handler
Handles contact form submissions from the website
"""

import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contact_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContactFormHandler:
    """Handles contact form submissions for Western Heights Inc."""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize with configuration"""
        self.config = self.load_config(config_file)
        self.submissions_dir = 'contact_submissions'
        self.setup_directories()
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "company_name": "Western Heights Inc.",
            "company_email": "info@westernheights.inc",
            "admin_email": "bdarlingtone@westernheights.inc",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "your_email@gmail.com",
            "smtp_password": "your_app_password",
            "save_to_file": True,
            "send_email": True
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                config = {**default_config, **config}
                logger.info(f"Configuration loaded from {config_file}")
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            config = default_config
            # Save default config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        return config
    
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.submissions_dir, exist_ok=True)
        logger.info(f"Created directory: {self.submissions_dir}")
    
    def validate_form_data(self, form_data: Dict) -> tuple:
        """Validate form data"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not form_data.get(field):
                errors.append(f"{field} is required")
        
        # Email validation
        email = form_data.get('email', '')
        if email and '@' not in email:
            errors.append("Invalid email address")
        
        # Phone validation (if provided)
        phone = form_data.get('phone', '')
        if phone and not phone.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            errors.append("Invalid phone number format")
        
        return len(errors) == 0, errors
    
    def save_submission(self, form_data: Dict):
        """Save form submission to file"""
        if not self.config.get('save_to_file', True):
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.submissions_dir}/submission_{timestamp}.json"
        
        # Add metadata
        submission_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': form_data.get('ip', 'Unknown'),
            'user_agent': form_data.get('user_agent', 'Unknown')
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(submission_data, f, indent=2)
            logger.info(f"Submission saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving submission: {e}")
            return None
    
    def generate_email_content(self, form_data: Dict) -> tuple:
        """Generate email subject and content"""
        subject = f"New Contact Form Submission: {form_data.get('name', 'Unknown')}"
        
        # HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0c5c46; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #0c5c46; }}
                .value {{ margin-top: 5px; padding: 10px; background-color: white; border: 1px solid #dee2e6; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Western Heights Inc.</h1>
                    <h2>New Contact Form Submission</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">Name:</div>
                        <div class="value">{form_data.get('name', 'Not provided')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value">{form_data.get('email', 'Not provided')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Phone:</div>
                        <div class="value">{form_data.get('phone', 'Not provided')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Company:</div>
                        <div class="value">{form_data.get('company', 'Not provided')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Service Interest:</div>
                        <div class="value">{form_data.get('service', 'Not specified')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Message:</div>
                        <div class="value">{form_data.get('message', 'Not provided')}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>This message was sent from the Western Heights Inc. website contact form.</p>
                    <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text content for email clients that don't support HTML
        text_content = f"""
        NEW CONTACT FORM SUBMISSION - Western Heights Inc.
        ===================================================
        
        Name: {form_data.get('name', 'Not provided')}
        Email: {form_data.get('email', 'Not provided')}
        Phone: {form_data.get('phone', 'Not provided')}
        Company: {form_data.get('company', 'Not provided')}
        Service Interest: {form_data.get('service', 'Not specified')}
        
        Message:
        {form_data.get('message', 'Not provided')}
        
        ---
        Sent from Western Heights Inc. website
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return subject, text_content, html_content
    
    def send_email(self, form_data: Dict) -> bool:
        """Send email notification"""
        if not self.config.get('send_email', True):
            logger.info("Email sending is disabled in config")
            return True
        
        try:
            subject, text_content, html_content = self.generate_email_content(form_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config['company_email']
            msg['To'] = self.config['admin_email']
            
            # Attach both HTML and plain text versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_username'], self.config['smtp_password'])
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {self.config['admin_email']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_auto_reply(self, form_data: Dict) -> bool:
        """Send auto-reply to the user"""
        try:
            user_email = form_data.get('email')
            if not user_email:
                return False
            
            subject = "Thank you for contacting Western Heights Inc."
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0c5c46 0%, #1a7d5e 100%); color: white; padding: 30px; text-align: center; }}
                    .gold {{ color: #d4af37; font-weight: bold; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; border: 1px solid #e9ecef; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #d4af37 0%, #f8c537 100%); color: black; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Western Heights Inc.</h1>
                        <h2><span class="gold">Elevating Innovation</span></h2>
                    </div>
                    <div class="content">
                        <h3>Dear {form_data.get('name', 'Valued Customer')},</h3>
                        
                        <p>Thank you for contacting <strong>Western Heights Inc.</strong> We have received your inquiry and our team will review it shortly.</p>
                        
                        <p>Here's a summary of your submission:</p>
                        <ul>
                            <li><strong>Service Interest:</strong> {form_data.get('service', 'General Inquiry')}</li>
                            <li><strong>Submitted:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</li>
                        </ul>
                        
                        <p><strong>What happens next?</strong></p>
                        <ol>
                            <li>Our team will review your inquiry within 24 hours</li>
                            <li>We'll contact you using the provided contact information</li>
                            <li>We'll schedule a consultation to discuss your specific needs</li>
                        </ol>
                        
                        <p>In the meantime, you can:</p>
                        <ul>
                            <li><a href="https://yourwebsite.com/services">Explore our services</a></li>
                            <li><a href="https://yourwebsite.com/resources">Download resources</a></li>
                            <li><a href="https://yourwebsite.com/contact">Visit our contact page</a></li>
                        </ul>
                        
                        <center>
                            <a href="https://yourwebsite.com" class="cta-button">Visit Our Website</a>
                        </center>
                        
                        <p><strong>Our Contact Information:</strong></p>
                        <p>📞 Phone: +265 884 560 048<br>
                        📧 Email: bdarlingtone@westernheights.inc<br>
                        🌐 Website: https://westernheights.inc</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated response. Please do not reply to this email.</p>
                        <p>© 2023 Western Heights Inc. | Elevating Innovation across Africa</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config['company_email']
            msg['To'] = user_email
            
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_username'], self.config['smtp_password'])
                server.send_message(msg)
            
            logger.info(f"Auto-reply sent to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending auto-reply: {e}")
            return False
    
    def process_form(self, form_data: Dict) -> Dict:
        """Main method to process form submission"""
        logger.info(f"Processing form submission from {form_data.get('name', 'Unknown')}")
        
        # Validate form data
        is_valid, errors = self.validate_form_data(form_data)
        if not is_valid:
            logger.warning(f"Form validation failed: {errors}")
            return {
                'success': False,
                'errors': errors,
                'message': 'Form validation failed'
            }
        
        # Save submission
        saved_file = self.save_submission(form_data)
        
        # Send notifications
        email_sent = self.send_email(form_data)
        auto_reply_sent = self.send_auto_reply(form_data)
        
        # Prepare response
        response = {
            'success': True,
            'message': 'Thank you for your message! We will contact you shortly.',
            'submission_id': saved_file,
            'email_sent': email_sent,
            'auto_reply_sent': auto_reply_sent,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Form processed successfully for {form_data.get('name')}")
        return response

# Example usage with Flask web framework
if __name__ == "__main__":
    # Example of how to use with Flask
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    handler = ContactFormHandler()
    
    @app.route('/api/contact', methods=['POST'])
    def contact_endpoint():
        """API endpoint for contact form submissions"""
        try:
            # Get form data
            form_data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'company': request.form.get('company'),
                'service': request.form.get('service'),
                'message': request.form.get('message'),
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }
            
            # Process form
            result = handler.process_form(form_data)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    # Run the server
    print("Starting contact form handler server...")
    print("Access the API at: http://localhost:5000/api/contact")
    app.run(debug=True, port=5000)