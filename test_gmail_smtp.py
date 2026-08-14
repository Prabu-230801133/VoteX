import smtplib
import os

HOST = "smtp.gmail.com"
PORT = 587

EMAIL = os.environ["EMAIL_HOST_USER"]
PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]

with smtplib.SMTP(HOST, PORT, timeout=15) as server:
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(EMAIL, PASSWORD)

print("GMAIL SMTP LOGIN SUCCESS")