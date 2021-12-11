#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from datetime import date
from time import sleep
from typing import List
from appointment import Appointment
import os
import requests
import json
import impfTwitter
import impfEmail

load_dotenv('impf-configuration.env')

STOPFILE_NAME = 'stopTheCount'
TODAY = date.today()
year = TODAY.year
kw = TODAY.isocalendar()[1]
impfPlaces = json.loads(os.environ.get('impfPlaces'))
TWEET_MAX_CHARS = 280


def _get_data(kw, year, url):
    params = dict(KW=kw, JAHR=year)
    resp = requests.get(url=url, params=params)
    return resp.json()


def _is_free_appointment(tag):
    return tag['TERMIN_STATUS'] != 1 and tag['TERMIN_STATUS'] != 2 and tag['TERMIN_STATUS'] != 3


def _condense_appointments(free_appointments):
    condensed_apps = {}
    for app in free_appointments:
        day = app.tag
        condensed_apps[day] = ""
    for app in free_appointments:
        if condensed_apps[app.tag] == "":
            condensed_apps[app.tag] = app.uhrzeit
        else:
            condensed_apps[app.tag] += ", " + app.uhrzeit
    return condensed_apps


def _search_for_appointment(data, frontend_url):
    free_appointments: List[Appointment] = []
    for timeSlot in data:
        for day in timeSlot['SPENDE_TERMIN']:
            # print(f"Checking timeslot on day: {day['DATUM']}")
            if _is_free_appointment(day):
                free_appointments.append(Appointment(
                    day['DATUM'], day['OEFFNUNGSZEIT']))

    if len(free_appointments) != 0:
        condensed_appointments = _condense_appointments(free_appointments)
        impfEmail.send_mails(condensed_appointments, frontend_url)
        impfTwitter.send_tweets(frontend_url, condensed_appointments)
        return True

    return False


found_any = False
for impfPlace in impfPlaces:
    kw = TODAY.isocalendar()[1]
    year = TODAY.year
    while not os.path.isfile(STOPFILE_NAME):
        data = _get_data(kw, year, impfPlace['backend'])
        if not data:
            print(
                f"Can\'t find any appointments. KW {kw} for {impfPlace['backend']} is not online.")
            break
        print(f"Checking {impfPlace['backend']}KW={kw}&JAHR={year}")
        found = _search_for_appointment(data, impfPlace['frontend'])
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
    sleep(60 * 15)
    os.remove(STOPFILE_NAME)
