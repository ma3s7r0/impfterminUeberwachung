#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
from datetime import date
from time import sleep
from email.message import EmailMessage
import smtplib
import ssl
import os
import requests
import json


load_dotenv('impf-configuration.env')
# Create a secure SSL context
context = ssl.create_default_context()
context.check_hostname = False


STOPFILE_NAME = 'stopTheCount'
TODAY = date.today()
year = TODAY.year
kw = TODAY.isocalendar()[1]
baseUrl = 'https://backend.impfen-ka.de/api.php/terminportal/getWochenAnsicht?'

SENDER = os.environ.get('eMailUser')
SUBSCRIBERS = os.environ.get('subscribers').split(",")


def getData(kw, year):
    params = dict(KW=kw, JAHR=year)
    resp = requests.get(url=baseUrl, params=params)
    return resp.json()


def sendMails(messages):
    with smtplib.SMTP_SSL(os.environ.get('eMailSMTP'), os.environ.get('eMailPort'), context=context) as server:
        print(
            f"Connecting to {os.environ.get('eMailSMTP')} as {SENDER}. Sending {len(messages)} eMails.")
        server.login(SENDER,
                     os.environ.get('eMailPassword'))
        for message in messages:
            print(f"Sending eMail to {message['To']}.")
            server.send_message(message)


def buildEmail(subscriber, subject, content):
    message = EmailMessage()
    message['From'] = SENDER
    message['To'] = subscriber
    message['Subject'] = subject
    message.set_content(content)
    return message


def sendToSubscribers(subscribers, subject, content):
    messages = []
    for subscriber in subscribers:
        messages.append(buildEmail(subscriber, subject, content))
    return messages


def isFreeAppointment(tag):
    return tag['TERMIN_STATUS'] != 1 and tag['TERMIN_STATUS'] != 2 and tag['TERMIN_STATUS'] != 3


def searchForAppointment(data):
    for timeSlot in data:
        print(f"Checking timeslot: {timeSlot['OEFFNUNGSZEIT']}")
        for tag in timeSlot['SPENDE_TERMIN']:
            print(f"Checking timeslot on day: {tag['DATUM']}")
            print(tag['TERMIN_STATUS'], tag['TEXT'])
            if isFreeAppointment(tag):
                subject = f'''Freier Impftermin {tag['DATUM']} um {tag['OEFFNUNGSZEIT']}'''
                content = f'''Es gibt einen freien Termin am {tag['DATUM']} um {tag['OEFFNUNGSZEIT']}.\nGo to https://www.impfen-eceka.de/#/desktop-view and get it. Fast!'''
                messages = sendToSubscribers(SUBSCRIBERS, subject, content)
                sendMails(messages)
                fp = open(STOPFILE_NAME, 'x')
                fp.close()
                print("Found an appointment. Sent an eMail. Now sleeping for an hour.")
                sleep(60*60)
                os.remove(STOPFILE_NAME)
                return True
    return False


while not os.path.isfile(STOPFILE_NAME):
    data = getData(kw, year)
    if not data:
        print(f'Can\'t find any appointments. KW {kw} is not online.')
        break
    print(f'Checking KW:{kw} year:{year}')
    found = searchForAppointment(data)
    if found:
        break
    kw += 1
    nextYear, kw = divmod(kw, 53)
    if nextYear:
        year += 1
