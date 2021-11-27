#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import date
from time import sleep
from email.message import EmailMessage
from pprint import pprint
from typing import List
import smtplib
import ssl
import os
import requests
import json
import tweepy


load_dotenv('impf-configuration.env')
# Create a secure SSL context
context = ssl.create_default_context()
context.check_hostname = False


STOPFILE_NAME = 'stopTheCount'
TODAY = date.today()
year = TODAY.year
kw = TODAY.isocalendar()[1]
impfPlaces = json.loads(os.environ.get('impfPlaces'))
TWEET_MAX_CHARS = 280


SENDER = os.environ.get('eMailUser')
SUBSCRIBERS = os.environ.get('subscribers').split(",")


@dataclass
class Appointment(object):
    tag: str
    uhrzeit: str

    def pretty_print_one_line(self):
        return f"am {self.tag} um {self.uhrzeit}\n"

    def same_day(self, otherApp):
        return self.day == otherApp.day


def getData(kw, year, url):
    params = dict(KW=kw, JAHR=year)
    resp = requests.get(url=url, params=params)
    return resp.json()


def sendMails(messages):
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


def send_tweets(tweets):
    try:
        # Create API object
        api = tweepy.Client(os.environ.get('bearer_token'), os.environ.get(
            'api_key'), os.environ.get('api_key_secret'), os.environ.get('access_token'),
            os.environ.get('access_token_secret'))

        # Create tweets
        last_tweet = 0
        for tweet in tweets:
            if last_tweet == 0:
                last_tweet = api.create_tweet(
                    text=tweet)
            else:
                last_tweet = api.create_tweet(
                    text=tweet, in_reply_to_tweet_id=last_tweet.data['id'])
    except Exception as e:
        print(e)


def buildEmail(subscriber, subject, content):
    message = EmailMessage()
    message['From'] = SENDER
    message['To'] = subscriber
    message['Subject'] = subject
    message.set_content(content)
    return message


def buildForAllSubscribers(subscribers, subject, content):
    messages = []
    for subscriber in subscribers:
        messages.append(buildEmail(subscriber, subject, content))
    return messages


def isFreeAppointment(tag):
    return tag['TERMIN_STATUS'] != 1 and tag['TERMIN_STATUS'] != 2 and tag['TERMIN_STATUS'] != 3


def searchForAppointment(data, frontendUrl):
    free_appointments: List[Appointment] = []
    for timeSlot in data:
        for day in timeSlot['SPENDE_TERMIN']:
            #print(f"Checking timeslot on day: {day['DATUM']}")
            if isFreeAppointment(day):
                free_appointments.append(Appointment(
                    day['DATUM'], day['OEFFNUNGSZEIT']))
    if len(free_appointments) != 0:
        sumApps = {}
        for app in free_appointments:
            day = app.tag
            sumApps[day] = ""
        for app in free_appointments:
            if sumApps[app.tag] == "":
                sumApps[app.tag] = app.uhrzeit
            else:
                sumApps[app.tag] += ", " + app.uhrzeit

        subject = f'''Freie Impftermine'''
        content = f'''Es gibt freie Termine: {sumApps}.\n Ab gehts zu {frontendUrl}. Auffi!'''

        messages = buildForAllSubscribers(SUBSCRIBERS, subject, content)
        pprint(messages)
        sendMails(messages)

        tweet_start = f'''Es gibt freie Impftermine!\n'''
        tweet_end = f"\nAb gehts zu {frontendUrl}. Auffi!"
        free_chars_for_appointment = TWEET_MAX_CHARS - \
            len(tweet_start) - len(tweet_end)
        tweets = []
        for day, uhrzeiten in sumApps.items():
            papp = f"Am {day} um {uhrzeiten}"
            tweet = tweet_start + papp + tweet_end
            tweets.append(tweet)
        send_tweets(tweets)
        print(f"Tweeted {tweets}")
        return True
    return False


found_any = False
for impfPlace in impfPlaces:
    kw = TODAY.isocalendar()[1]
    while not os.path.isfile(STOPFILE_NAME):
        data = getData(kw, year, impfPlace['backend'])
        if not data:
            print(
                f"Can\'t find any appointments. KW {kw} for {impfPlace['backend']} is not online.")
            break
        print(f"Checking KW:{kw} year:{year} in {impfPlace['backend']}")
        found = searchForAppointment(data, impfPlace['frontend'])
        if found:
            found_any = True
        kw += 1
        nextYear, kw = divmod(kw, 53)
        if nextYear:
            year += 1

if found_any:
    fp = open(STOPFILE_NAME, 'x')
    fp.close()
    print("Found at least one appointment. Sent eMails and tweet. Now sleeping for an 1/4 hour.")
    sleep(60*15)
    os.remove(STOPFILE_NAME)
