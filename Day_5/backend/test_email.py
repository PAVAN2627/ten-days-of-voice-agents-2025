"""
Test script to diagnose email sending issues
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

def test_email_connection():
    """Test SMTP connection and email sending"""
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "")
    sender_password = os.getenv("SENDER_PASSWORD", "")
    sender_name = os.getenv("SENDER_NAME", "Priya - Razorpay SDR")
    
    print("=" * 60)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 60)
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Sender Email: {sender_email}")
    print(f"Sender Name: {sender_name}")
    print(f"Password Present: {'Yes' if sender_password else 'No'}")
    print(f"Password Length: {len(sender_password) if sender_password else 0}")
    print("=" * 60)
    
    if not sender_email or not sender_password:
        print("\n❌ ERROR: Missing email credentials in .env.local")
        return False
    
    # Test recipient (send to same email for testing)
    recipient_email = input(f"\nEnter recipient email (press Enter to use {sender_email}): ").strip()
    if not recipient_email:
        recipient_email = sender_email
    
    print(f"\n📧 Attempting to send test email to: {recipient_email}")
    print("-" * 60)
    
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg["From"] = formataddr((sender_name, sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = "🧪 Test Email from Razorpay SDR Agent"
        
        # Simple text body
        text_body = """
Hello!

This is a test email from the Razorpay SDR Voice Agent.

If you're receiving this, the email configuration is working correctly! ✅

Best regards,
Priya
Razorpay SDR Agent
"""
        
        # HTML body
        html_body = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; }
        .content { padding: 20px; background: #f9f9f9; border-radius: 8px; margin-top: 20px; }
        .success { background: #10b981; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Email</h1>
            <p>Razorpay SDR Voice Agent</p>
        </div>
        <div class="content">
            <h2>Hello!</h2>
            <p>This is a test email from the Razorpay SDR Voice Agent.</p>
            <div class="success">
                ✅ Email Configuration Working!
            </div>
            <p>If you're receiving this, the email system is properly configured and functioning.</p>
            <p><strong>Best regards,</strong><br>
            Priya<br>
            Razorpay SDR Agent</p>
        </div>
    </div>
</body>
</html>
"""
        
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Connect and send
        print("🔌 Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            print("✅ Connected to SMTP server")
            
            print("🔐 Starting TLS encryption...")
            server.starttls()
            print("✅ TLS encryption enabled")
            
            print("🔑 Logging in...")
            server.login(sender_email, sender_password)
            print("✅ Login successful")
            
            print("📤 Sending email...")
            server.send_message(msg)
            print("✅ Email sent successfully!")
        
        print("-" * 60)
        print(f"\n✅ SUCCESS! Test email sent to {recipient_email}")
        print("\n📬 Check your inbox (and spam folder) for the test email.")
        print("\nIf you don't receive it within 2-3 minutes, check:")
        print("  1. Gmail App Password is correct")
        print("  2. 2-Factor Authentication is enabled on Gmail")
        print("  3. Spam/Junk folder")
        print("  4. Gmail security settings")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {e}")
        print("\n🔧 SOLUTIONS:")
        print("  1. Verify your Gmail App Password is correct")
        print("  2. Make sure 2-Factor Authentication is enabled")
        print("  3. Generate a new App Password at: https://myaccount.google.com/apppasswords")
        print("  4. Update SENDER_PASSWORD in .env.local")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR: {e}")
        print("\n🔧 Check your SMTP settings and try again")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting email configuration test...\n")
    success = test_email_connection()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ EMAIL SYSTEM IS WORKING CORRECTLY")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ EMAIL SYSTEM NEEDS CONFIGURATION")
        print("=" * 60)
