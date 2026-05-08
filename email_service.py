from flask import current_app
from flask_mail import Mail, Message
import os

class EmailService:
    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        # Configure mail settings
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@truedisciple.rw')
        
        self.mail = Mail(app)
    
    def send_password_reset_email(self, user_email, reset_link):
        """Send password reset email"""
        try:
            msg = Message(
                'Password Reset Request - AbideWord',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user_email]
            )
            
            msg.body = f'''
                Hello,

                You requested a password reset for your AbideWord account.

                Click the following link to reset your password:
                {reset_link}

                This link will expire in 1 hour for security reasons.

                If you didn't request this password reset, please ignore this email.

                Thank you,
                AbideWord Team
                            '''
            
            msg.html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - AbideWord</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; line-height: 1.6;">
    
    <div style="max-width: 600px; margin: 40px auto; background: linear-gradient(135deg, #FAEEDA 0%, #f0f4f8 100%); border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: #2c3e50; padding: 30px; text-align: center;">
            <h1 style="color: #FAEEDA; margin: 0; font-size: 28px; font-weight: 600;">AbideWord</h1>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px; background: white;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 20px; font-weight: 600;">Password Reset Request</h2>
                <p style="color: #6c757d; margin: 0; font-size: 16px;">Secure access to your ministry account</p>
            </div>
            
            <div style="background: #f8f9fa; border-left: 4px solid #EF9F27; padding: 20px; border-radius: 0 8px 8px 0; margin: 25px 0;">
                <p style="margin: 0; color: #495057; font-size: 16px;">
                    <strong style="color: #2c3e50;">Hello,</strong><br>
                    We received a request to reset the password for your AbideWord account. Click the button below to securely reset your password.
                </p>
            </div>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{reset_link}" 
                   style="background: linear-gradient(135deg, #EF9F27, #f39c12); 
                          color: white; 
                          padding: 16px 40px; 
                          text-decoration: none; 
                          border-radius: 8px; 
                          display: inline-block; 
                          font-weight: 600; 
                          font-size: 16px;
                          box-shadow: 0 4px 15px rgba(239, 159, 39, 0.3);
                          transition: all 0.3s ease;">
                    🔄 Reset My Password
                </a>
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 25px 0;">
                <p style="margin: 0; color: #856404; font-size: 14px; text-align: center;">
                    <strong>⏰ Security Notice:</strong> This link will expire in <strong>1 hour</strong> for your protection.
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef;">
                <p style="margin: 0 0 10px 0; color: #6c757d; font-size: 14px;">
                    <strong>🔒 Didn't request this?</strong><br>
                    If you didn't request a password reset, please ignore this email. Your account remains secure.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #2c3e50; padding: 25px; text-align: center;">
            <p style="color: #FAEEDA; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">
                AbideWord Ministry Platform
            </p>
            <p style="color: #b8c5d6; margin: 0; font-size: 12px;">
                Empowering digital ministry • Serving faith communities worldwide
            </p>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #34495e;">
                <p style="color: #95a5a6; margin: 0; font-size: 11px;">
                    © 2024 AbideWord. All rights reserved. | Privacy Policy | Terms of Service
                </p>
            </div>
        </div>
    </div>
</body>
</html>
            '''
            
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

# Create a global instance
email_service = EmailService()
