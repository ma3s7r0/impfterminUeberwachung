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
import logging

load_dotenv('impf-configuration.env')
logging.basicConfig(filename='impfUeberwachung.log', level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger("Main")

STOPFILE_NAME = 'stopTheCount'
TODAY = date.today()
impfPlaces = json.loads(os.environ.get('impfPlaces'))
TWEET_MAX_CHARS = 280


def _get_data(act_kw, act_year, url):
    params = dict(KW=act_kw, JAHR=act_year)
    resp = requests.get(url=url, params=params)
    return resp.json()


def _is_free_appointment(tag):
    return tag['FREIE_LIEGEN_DAUERSPENDER'] != '-1' and tag['TERMIN_STATUS'] != 1 and tag['TERMIN_STATUS'] != 2 and tag['TERMIN_STATUS'] != 3


def _condense_appointments(free_appointments):
    condensed_apps = {}
    for app in free_appointments:
        day = app.tag
        condensed_apps[day] = []
    for app in free_appointments:
        condensed_apps[app.tag].append(app.uhrzeit)
    return condensed_apps


def _search_for_appointment(act_data, frontend_url):
    free_appointments: List[Appointment] = []
    for timeSlot in act_data:
        for day in timeSlot['SPENDE_TERMIN']:
            # logger.info(f"Checking timeslot on day: {day['DATUM']}")
            if _is_free_appointment(day):
                free_appointments.append(Appointment(
                    day['DATUM'], day['OEFFNUNGSZEIT']))

    if len(free_appointments) != 0:
        condensed_appointments = _condense_appointments(free_appointments)
        impfEmail.send_mails(condensed_appointments, frontend_url)
        impfTwitter.send_tweets(frontend_url, condensed_appointments)
        return True

    return False


if __name__ == "__main__":
    found_any = False
    for impfPlace in impfPlaces:
        kw = TODAY.isocalendar()[1]
        year = TODAY.year
        while not os.path.isfile(STOPFILE_NAME):
            data = _get_data(kw, year, impfPlace['backend'])
            if not data:
                logger.info(
                    f"Can\'t find any appointments. KW {kw} for {impfPlace['backend']} is not online.")
                break
            logger.info(f"Checking {impfPlace['backend']}KW={kw}&JAHR={year}")
            found = _search_for_appointment(data, impfPlace['frontend'])
            if found:
                found_any = True
            nextYear, kw = divmod(kw, 52)
            kw += 1
            if nextYear:
                year += 1

    if found_any:
        fp = open(STOPFILE_NAME, 'x')
        fp.close()
        logger.info("Found at least one appointment. Sent eMails and tweet. Now sleeping for an hour.")
        sleep(60 * 60)
        os.remove(STOPFILE_NAME)
