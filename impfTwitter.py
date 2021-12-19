from time import sleep

import tweepy
from dotenv import load_dotenv
import os
import logging

load_dotenv('impf-configuration.env')
logger = logging.getLogger(__name__)


def send_tweets(frontend_url, condensed_apps):
    tweets = _build_tweets(frontend_url, condensed_apps)
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
        logger.info(f"Tweeted {tweets}")
    except Exception as e:
        logger.error(e)


def _build_tweets(frontend_url, free_appointments):
    usedChars = 0
    tweet_start = f'''Es gibt freie Impftermine!\n'''
    usedChars += len(tweet_start)
    tweet_end = f"\nAb gehts zu {frontend_url}. Auffi!"
    usedChars += len(tweet_start)
    tweets = []
    for day, uhrzeiten in free_appointments.items():
        uhrzeiten_part = ""
        for uhrzeit in uhrzeiten:
            if uhrzeiten_part == "":
                uhrzeiten_part = uhrzeit
            else:
                uhrzeiten_part += ", " + uhrzeit
            if len(uhrzeiten_part) > 210 - usedChars:
                papp = f"Am {day} um {uhrzeiten_part}"
                tweet = tweet_start + papp + tweet_end
                tweets.append(tweet)
                uhrzeiten_part = ""

        if uhrzeiten_part != "":
            papp = f"Am {day} um {uhrzeiten_part}"
            tweet = tweet_start + papp + tweet_end
            tweets.append(tweet)

    return tweets
