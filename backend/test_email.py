import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()


def test_email():
    try:
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))

        msg = MIMEText("Test email from JeffreyWoo Price Comparison System")
        msg["Subject"] = "Test Notification"
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = "your-test-email@gmail.com"

        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")


if __name__ == "__main__":
    test_email()