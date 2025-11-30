"""
Email Service for Order Confirmations
Sends automatic email notifications when orders are placed
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order: dict, user_email: str, user_name: str) -> bool:
    """
    Send order confirmation email to customer
    
    Args:
        order: Order dictionary with id, line_items, total_amount, etc.
        user_email: Customer email address
        user_name: Customer name
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Get email configuration from environment
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "")
    sender_password = os.getenv("SENDER_PASSWORD", "")
    sender_name = os.getenv("SENDER_NAME", "E-Commerce Store")
    
    if not sender_email or not sender_password:
        logger.warning("Email configuration missing. Skipping email send.")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = user_email
        msg['Subject'] = f"Order Confirmation - {order['id']}"
        
        # Create HTML email body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .order-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .order-info h2 {{
            color: #667eea;
            margin-top: 0;
        }}
        .order-details {{
            margin: 15px 0;
        }}
        .order-details p {{
            margin: 8px 0;
        }}
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        .items-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .items-table td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        .items-table tr:last-child td {{
            border-bottom: none;
        }}
        .total-row {{
            background: #f0f0f0;
            font-weight: bold;
            font-size: 18px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            background: #fbbf24;
            color: #78350f;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Order Confirmed!</h1>
        <p>Thank you for your purchase, {user_name}!</p>
    </div>
    
    <div class="content">
        <div class="order-info">
            <h2>Order Details</h2>
            <div class="order-details">
                <p><strong>Order ID:</strong> {order['id']}</p>
                <p><strong>Order Date:</strong> {datetime.fromisoformat(order['created_at']).strftime('%B %d, %Y at %I:%M %p')}</p>
                <p><strong>Status:</strong> <span class="status-badge">{order['status']}</span></p>
            </div>
        </div>
        
        <h3>Items Ordered:</h3>
        <table class="items-table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add line items
        for item in order['line_items']:
            item_name = item['name']
            # Add size if available
            if 'size' in item and item['size']:
                item_name += f" (Size: {item['size']})"
            
            html_body += f"""
                <tr>
                    <td>{item_name}</td>
                    <td>{item['quantity']}</td>
                    <td>₹{item['unit_amount']:.2f}</td>
                    <td>₹{item['line_total']:.2f}</td>
                </tr>
"""
        
        # Add total
        html_body += f"""
                <tr class="total-row">
                    <td colspan="3">Total Amount</td>
                    <td>₹{order['total_amount']:.2f}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="order-info">
            <h2>Delivery Information</h2>
            <div class="order-details">
                <p><strong>Name:</strong> {order['buyer']['name']}</p>
                <p><strong>Email:</strong> {order['buyer']['email']}</p>
                <p><strong>Phone:</strong> {order['buyer']['phone']}</p>
                <p><strong>Address:</strong> {order['buyer']['address']}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Thank you for shopping with {sender_name}!</p>
            <p>If you have any questions, please reply to this email.</p>
            <p style="font-size: 12px; color: #999;">
                This is an automated email. Please do not reply directly to this message.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        logger.info(f"📧 Sending order confirmation email to {user_email}")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        logger.info(f"✅ Order confirmation email sent successfully to {user_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed: {str(e)}")
        logger.error("   Check SENDER_EMAIL and SENDER_PASSWORD in .env.local")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        return False


def test_email_configuration() -> bool:
    """Test email configuration"""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "")
    sender_password = os.getenv("SENDER_PASSWORD", "")
    
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION TEST")
    print("="*60)
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Sender Email: {sender_email}")
    print(f"Password: {'*' * len(sender_password) if sender_password else 'NOT SET'}")
    print("="*60 + "\n")
    
    if not sender_email or not sender_password:
        print("❌ Email configuration incomplete!")
        print("   Set SENDER_EMAIL and SENDER_PASSWORD in .env.local")
        return False
    
    try:
        print("🔌 Testing SMTP connection...")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            print("✅ Connected to SMTP server")
            server.starttls()
            print("✅ TLS encryption started")
            server.login(sender_email, sender_password)
            print("✅ Authentication successful")
        
        print("\n✅ Email configuration is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Email configuration test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Test email configuration
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    test_email_configuration()
