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
    free_apps = []
    for day, uhrzeiten in condensed_appointments.items():
        free_app = f'''{day} um '''
        uhrzeiten_part = ""
        for uhrzeit in uhrzeiten:
            if uhrzeiten_part == "":
                uhrzeiten_part = uhrzeit
            else:
                uhrzeiten_part += ", " + uhrzeit
        free_app += uhrzeiten_part + '''\n'''
        free_apps.append(free_app)

    content = f'''Es gibt freie Termine am {free_apps}.\n Ab gehts zu {frontend_url}. Auffi!'''

    messages = _build_for_all_subscribers(subject, content)
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


def _build_email(subscriber, subject, content):
    message = EmailMessage()
    message['From'] = SENDER
    message['To'] = subscriber
    message['Subject'] = subject
    message.set_content(content)
    return message


def _build_for_all_subscribers(subject, content):
    messages = []
    for subscriber in SUBSCRIBERS:
        messages.append(_build_email(subscriber, subject, content))
    return messages
