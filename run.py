#!/usr/bin/env python3

import helpers
import logging
import sys
import tweettoot
import traceback

# Initialize common logging options
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def runJob(tweet_url):
    config = "config.json"

    # Initialize variables
    app_name = helpers._config("TT_APP_NAME", config)
    twitter_url = tweet_url
    mastodon_url = helpers._config("TT_HOST_INSTANCE", config)
    mastodon_token = helpers._config("TT_APP_SECURE_TOKEN", config)
    twitter_guest_token = helpers._config("TT_TWITTER_GUEST_TOKEN", config)
    twitter_user_agent = helpers._config("TT_TWITTER_USER_AGENT", config)

    strip_urls = False
    if (helpers._config("TT_STRIP_URLS", config).lower() == "yes"):
        strip_urls = True

    try:
        job = tweettoot.TweetToot(
            app_name=app_name,
            twitter_url=twitter_url,
            mastodon_url=mastodon_url,
            mastodon_token=mastodon_token,
            twitter_guest_token=twitter_guest_token,
            twitter_user_agent=twitter_user_agent,
            strip_urls=strip_urls,
        )
        job.relay()
    except Exception as e:
        logger.critical(e)
        traceback.print_exc()

    return True


if __name__ == "__main__":
    runJob(sys.argv[1])
