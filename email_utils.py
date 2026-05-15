import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, body):

    from dotenv import load_dotenv
    import os
    load_dotenv()
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        print("Email failed:", e)
        return False