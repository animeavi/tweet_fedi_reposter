#!/usr/bin/env python3

from mastodon import Mastodon
from tweepy import API
from tweepy import OAuthHandler
import helpers
import html
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
    twitter_api_key = ""
    twitter_api_secret = ""
    twitter_user_key = ""
    twitter_user_secret = ""
    strip_urls = False
    remove_url_re = r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b'
    twitter_username_re = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')
    logger_prefix = ""

    def __init__(self, app_name: str, twitter_url: str, mastodon_url: str, mastodon_token: str,
                twitter_api_key: str, twitter_api_secret: str, twitter_user_key: str,
                twitter_user_secret: str, strip_urls: bool):
        self.app_name = app_name
        self.twitter_url = twitter_url
        self.mastodon_url = mastodon_url
        self.mastodon_token = mastodon_token
        self.twitter_api_key = twitter_api_key
        self.twitter_api_secret = twitter_api_secret
        self.twitter_user_key = twitter_user_key
        self.twitter_user_secret = twitter_user_secret
        self.strip_urls = strip_urls
        self.logger_prefix = self.app_name + " - "

    def relay(self):
        logger.info(self.logger_prefix + "Reposting " + self.twitter_url + " to " + self.mastodon_url + ".")

        auth = OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
        auth.set_access_token(self.twitter_user_key, self.twitter_user_secret)
        twitter_api = API(auth)

        tweet = twitter_api.get_status(int(self.twitter_url.split("/")[-1].split("?")[0]), tweet_mode="extended")

        tweet_text = self.get_tweet_text(tweet, twitter_api)
        tweet_text = html.unescape(tweet_text)
        tweet_text = self.escape_usernames(tweet_text)
        tweet_text = self.expand_urls(tweet, tweet_text, twitter_api)

        if self.strip_urls:
            tweet_text = self.remove_urls(tweet_text)

        tweet_media = self.get_tweet_media(tweet, twitter_api)

        # Only initialize the Mastodon API if we find something
        mastodon_api = Mastodon(
            access_token=self.mastodon_token,
            api_base_url=self.mastodon_url
        )

        media_ids = []
        for media in tweet_media:
            media_id = self.transfer_media(media, mastodon_api)
            if (media_id != -1):
                media_ids.append(media_id);
        post_id = -1
        post_id = self.post_tweet(media_ids, tweet_text, mastodon_api)
        if (post_id != -1):
            logger.info(self.logger_prefix + "Tweet posted to Mastodon successfully!")
        else:
            logger.error(self.logger_prefix + "Failed to post Tweet to Mastodon!")

    def get_tweet_entities(self, tweet, twitter_api, get_ext=True):
        entities = None

        if get_ext and 'extended_entities' in tweet._json:
            entities = tweet.extended_entities
        elif 'entities' in tweet._json:
            entities = tweet.entities

        return entities

    def get_tweet_media(self, tweet, twitter_api):
        media_list = []
        entities = self.get_tweet_entities(tweet, twitter_api)

        if entities is None:
            return media_list

        if 'media' in entities:
            for media in entities['media']:
                if media['type'] == 'video' or media['type'] == 'animated_gif':
                    media_list.append(self.get_best_media(media['video_info']['variants']))
                    break
                else:
                    media_list.append(media['media_url'])

        return media_list

    def get_best_media(self, media):
        higher_bitrate = -1
        media_url = ""

        for video in media:
            if (video['content_type'] == 'application/x-mpegURL'):
                continue

            if (video['bitrate'] > higher_bitrate):
                higher_bitrate = video['bitrate']
                media_url = video['url']

        return media_url

    def get_tweet_text(self, tweet, twitter_api):
        text = ""
        remove_media_url = ""
        entities = self.get_tweet_entities(tweet, twitter_api)

        if hasattr(tweet, 'full_text'):
            text = tweet.full_text
        elif hasattr(tweet, 'text'):
            text = tweet.text

        text = "RT @" + tweet.user.screen_name + ": " + text

        if 'media' in entities:
            remove_media_url = entities['media'][0]['url']

        return text.replace(remove_media_url, "")

    def expand_urls(self, tweet, tweet_text, twitter_api):
        text = tweet_text
        entities = self.get_tweet_entities(tweet, twitter_api, False)

        if entities is None:
            return text

        if 'urls' in entities:
            for url in entities['urls']:
                text = text.replace(url['url'], url['expanded_url'])

        return text

    def transfer_media(self, media_url, mastodon_api):
        media_id = -1

        logger.info(self.logger_prefix + "Downloading " + media_url)

        media_file = requests.get(media_url, stream=True)
        media_file.raw.decode_content = True

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(media_file.raw.read())
        temp_file.close()
        file_extension = mimetypes.guess_extension(media_file.headers['Content-type'])
        upload_file_name = temp_file.name + file_extension
        os.rename(temp_file.name, upload_file_name)
        temp_file_read = open(upload_file_name, 'rb')

        logger.info(self.logger_prefix + "Uploading " + media_url + " to Mastodon")

        media_id = mastodon_api.media_post(upload_file_name)["id"]

        temp_file_read.close()
        os.unlink(upload_file_name)

        return media_id

    def post_tweet(self, media_ids, tweet_text, mastodon_api):
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
        text = re.sub(self.remove_url_re, '', text, flags=re.MULTILINE)
        return text

    def escape_usernames(self, text):
        ats = re.findall(self.twitter_username_re, text)
        for at in ats:
            text = text.replace("@"+at, "@*"+at)

        return text
