import tweepy
from dotenv import load_dotenv
import os

load_dotenv('impf-configuration.env')


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
        print(f"Tweeted {tweets}")
    except Exception as e:
        print(e)


def _build_tweets(frontend_url, free_appointments):
    tweet_start = f'''Es gibt freie Impftermine!\n'''
    tweet_end = f"\nAb gehts zu {frontend_url}. Auffi!"
    tweets = []
    for day, uhrzeiten in free_appointments.items():
        papp = f"Am {day} um {uhrzeiten}"
        tweet = tweet_start + papp + tweet_end
        tweets.append(tweet)
