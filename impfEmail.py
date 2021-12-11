import smtplib
import ssl
from pprint import pprint
from dotenv import load_dotenv
import os
from email.message import EmailMessage


load_dotenv('impf-configuration.env')
# Create a secure SSL context
context = ssl.create_default_context()
context.check_hostname = False


SENDER = os.environ.get('eMailUser')
SUBSCRIBERS = os.environ.get('subscribers').split(",")


def send_mails(condensed_appointments, frontend_url):
    subject = f'''Freie Impftermine'''
    content = f'''Es gibt freie Termine: {condensed_appointments}.\n Ab gehts zu {frontend_url}. Auffi!'''

    messages = _buildForAllSubscribers(subject, content)
    pprint(messages)
    with smtplib.SMTP_SSL(os.environ.get('eMailSMTP'), os.environ.get('eMailPort'), context=context) as server:
        print(
            f"Connecting to {os.environ.get('eMailSMTP')} as {SENDER}. Sending {len(messages)} eMails.")
        try:
            server.login(SENDER, os.environ.get('eMailPassword'))
            for message in messages:
                print(f"Sending eMail to {message['To']}.")
                server.send_message(message)
        except Exception as e:
            print(e)
        server.close()


def _buildEmail(subscriber, subject, content):
    message = EmailMessage()
    message['From'] = SENDER
    message['To'] = subscriber
    message['Subject'] = subject
    message.set_content(content)
    return message


def _buildForAllSubscribers(subject, content):
    messages = []
    for subscriber in SUBSCRIBERS:
        messages.append(_buildEmail(subscriber, subject, content))
    return messages
