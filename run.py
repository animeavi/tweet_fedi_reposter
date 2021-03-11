#!/usr/bin/env python3

import helpers
import logging
import schedule
import sys
import time
import tweettoot

# Initialize common logging options
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize variables
app_name = helpers._config("TT_APP_NAME")
twitter_url = helpers._config("TT_SOURCE_TWITTER_URL")
mastodon_url = helpers._config("TT_HOST_INSTANCE")
mastodon_token = helpers._config("TT_APP_SECURE_TOKEN")
mastodon_client_id = helpers._config("TT_APP_CLIENT_ID")
mastodon_client_token = helpers._config("TT_APP_CLIENT_TOKEN")
twitter_user_id = helpers._config("TT_TWITTER_USER_ID")
twitter_api_key = helpers._config("TT_TWITTER_CONSUMER_KEY")
twitter_api_secret = helpers._config("TT_TWITTER_CONSUMER_SECRET")
twitter_user_key = helpers._config("TT_TWITTER_TOKEN")
twitter_user_secret = helpers._config("TT_TWITTER_TOKEN_SECRET")
every_x_minutes = helpers._config("TT_RUN_EVERY_X_MINUTES")

strip_urls = False
if (helpers._config("TT_STRIP_URLS").lower() == "yes"):
    strip_urls = True

twitter_url = twitter_url.replace('https://twitter', 'https://mobile.twitter')

def runJob():
    try:
        job = tweettoot.TweetToot(
            app_name = app_name,
            twitter_url = twitter_url,
            mastodon_url = mastodon_url,
            mastodon_token = mastodon_token,
            mastodon_client_id = mastodon_client_id,
            mastodon_client_token = mastodon_client_token,
            twitter_user_id = twitter_user_id,
            twitter_api_key = twitter_api_key,
            twitter_api_secret = twitter_api_secret,
            twitter_user_key = twitter_user_key,
            twitter_user_secret = twitter_user_secret,
            strip_urls = strip_urls
        )
        job.relay()
    except Exception as e:
        logger.critical(e)
        return false

    return True

if __name__ == "__main__":
    runJob()
    schedule.every(every_x_minutes).minutes.do(lambda: runJob())
    
    while 1:
        schedule.run_pending()
        time.sleep(1)    
