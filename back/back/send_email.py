import os

import smtplib
from email.message import EmailMessage

def send_email(user_code, email):
	msg = EmailMessage()
	msg.set_content(f"Hi! This is your verification code for user {user_code}")
	msg['subject'] = "2FA code for PongGame"
	msg['to'] = email

	user = os.getenv('TWO_FA_MAIL')
	msg['from'] = user
	password = os.getenv('TWO_FA_PASS')

	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login(user, password)
	server.send_message(msg)
	server.quit()