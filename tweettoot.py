#!/usr/bin/env python3

from mastodon import Mastodon
from tweepy import API
from tweepy import OAuthHandler
import helpers
import logging
import mimetypes
import os
import re
import requests
import tempfile

logger = logging.getLogger(__name__)

class TweetToot:
    app_name = ""
    twitter_url = ""
    mastodon_url = ""
    mastodon_token = ""
    mastodon_client_id = ""
    mastodon_client_token = ""
    twitter_user_id = 0
    twitter_api_key = ""
    twitter_api_secret = ""
    twitter_user_key = ""
    twitter_user_secret = ""
    strip_urls = True
    posted_ids = []

    def __init__(self, app_name: str, twitter_url: str, mastodon_url: str, mastodon_token: str,
                mastodon_client_id: str, mastodon_client_token: str, twitter_user_id: str,
                twitter_api_key: str, twitter_api_secret: str, twitter_user_key: str,
                twitter_user_secret: str, strip_urls: bool):
        self.app_name = app_name
        self.twitter_url = twitter_url
        self.mastodon_url = mastodon_url
        self.mastodon_token = mastodon_token
        self.mastodon_client_id = mastodon_client_id
        self.mastodon_client_token = mastodon_client_token
        self.twitter_user_id = twitter_user_id
        self.twitter_api_key = twitter_api_key
        self.twitter_api_secret = twitter_api_secret
        self.twitter_user_key = twitter_user_key
        self.twitter_user_secret = twitter_user_secret
        self.strip_urls = strip_urls
        self.posted_ids = self.read_posted_ids()
 
    def relay(self):
        if not self.app_name:
            logger.error(f"relay() => Application name in config is incorrect/empty.")
            return False

        if not self.twitter_url:
            logger.error(f"relay() => Twitter URL in config is incorrect/empty.")
            return False

        if not self.mastodon_url:
            logger.error(f"relay() => Mastodon URL in config is incorrect/empty.")
            return False

        if not self.mastodon_token:
            logger.error(f"relay() => Mastodon token in config is incorrect/empty.")
            return False
        # TODO: add more checks

        logger.info("Init relay from " + self.twitter_url + " to " + self.mastodon_url + ".")

        auth = OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
        auth.set_access_token(self.twitter_user_key, self.twitter_user_secret)
        twitter_api = API(auth)

        tweet = self.get_latest_tweet(twitter_api)

        if hasattr(tweet, 'retweeted_status'):
            logger.info("RT detected, skipping")
            return True

        tweet_id = tweet.id
        if str(tweet_id) in self.posted_ids:
            logger.info("Already posted, skipping")
            return True;

        tweet_text = self.get_tweet_text(tweet, twitter_api)
        if self.strip_urls:
            tweet_text = self.remove_urls(tweet_text)

        tweet_media = self.get_tweet_media(tweet, twitter_api)

        if not tweet_media:
            logger.info("No media found, skipping")
            return True

        # Only initialize the Mastodon API if we find something
        mastodon_api = Mastodon(
            client_id=self.mastodon_client_id,
            client_secret=self.mastodon_client_token,
            access_token=self.mastodon_token,
            api_base_url=self.mastodon_url
        )

        media_ids = []
        for media in tweet_media:
            media_id = self.transfer_media(media, mastodon_api)
            if (media_id != -1):
                media_ids.append(media_id);
        post_id = -1
        post_id = self.post_tweet(media_ids, tweet_text, tweet_id, mastodon_api)
        if (post_id != -1):
            logger.info("Tweet posted to Mastodon successfully!")
            self.update_posted_ids(str(tweet_id))
        else:
            logger.error("Failed to post Tweet to Mastodon!")

    def get_latest_tweet(self, twitter_api):
        # count: maximum allowed tweets count
        # tweet_mode: extended to get the full text,it prevents a primary tweet longer than 140 characters from being truncated.
        timeline = twitter_api.user_timeline(user_id=self.twitter_user_id, count=1, tweet_mode="extended")
        tweet = timeline[0]

        return tweet

    def get_tweet_media(self, tweet, twitter_api):
        media_list = []

        if 'media' in tweet.entities:
            for media in tweet.extended_entities['media']:
                if media['type'] == 'video':
                    media_list.append(media['video_info']['variants'][0]['url'])
                    break
                else:
                    media_list.append(media['media_url'])

        return media_list

    def get_tweet_text(self, tweet, twitter_api):
        text = ""
        if not hasattr(tweet, 'full_text'):
            return text

        text = tweet.full_text

        return text

    def transfer_media(self, media_url, mastodon_api):
        media_id = -1

        logger.info("Downloading " + media_url)

        media_file = requests.get(media_url, stream=True)
        media_file.raw.decode_content = True

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(media_file.raw.read())
        temp_file.close()
        file_extension = mimetypes.guess_extension(media_file.headers['Content-type'])
        upload_file_name = temp_file.name + file_extension
        os.rename(temp_file.name, upload_file_name)
        temp_file_read = open(upload_file_name, 'rb')

        logger.info("Uploading " + media_url + " to Mastodon")

        media_id = mastodon_api.media_post(upload_file_name)["id"]

        temp_file_read.close()
        os.unlink(upload_file_name)

        return media_id

    def post_tweet(self, media_ids, tweet_text, tweet_id, mastodon_api):
        post = mastodon_api.status_post(
            status = tweet_text,
            media_ids = media_ids,
            visibility = "public",
            sensitive = False,
            spoiler_text = None,
            in_reply_to_id = None
        )

        return post["id"]

    def remove_urls(self, text):
        text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
        return text\

    def read_posted_ids(self):
        lines = []
        with open("./posted.ids") as file:
            for line in file: 
                line = line.strip()
                lines.append(line)

        return lines

    def update_posted_ids(self, id):
        self.posted_ids.append(id)
        with open("posted.ids", "a") as file_object:
            file_object.write("\n" + id)
