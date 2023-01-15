#!/usr/bin/env python3

from mastodon import Mastodon
import codecs
import helpers
import html
import json
import logging
import mimetypes
import os
import random
import re
import requests
import string
import tempfile
import time

logger = logging.getLogger(__name__)


class TweetToot:
    app_name = ""
    twitter_url = ""
    mastodon_url = ""
    mastodon_token = ""
    twitter_guest_token = ""
    twitter_user_agent = ""
    strip_urls = False
    remove_url_re = r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b'
    twitter_username_re = re.compile(
        r'(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)')
    logger_prefix = ""
    tweet_user_name = ""
    twitter_session_headers = {}
    graphql_params = {
        "referrer": "tweet",
        "with_rux_injections": False,
        "includePromotedContent": False,
        "withCommunity": False,
        "withQuickPromoteEligibilityTweetFields": False,
        "withTweetQuoteCount": False,
        "withBirdwatchNotes": False,
        "withSuperFollowsUserFields": False,
        "withBirdwatchPivots": False,
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withSuperFollowsTweetFields": False,
        "withVoice": False,
        "withV2Timeline": False,
        "__fs_interactive_text": False,
        "__fs_dont_mention_me_view_api_enabled": False
    }

    def __init__(
            self,
            app_name: str,
            twitter_url: str,
            mastodon_url: str,
            mastodon_token: str,
            twitter_guest_token: str,
            twitter_user_agent: str,
            strip_urls: bool):
        self.app_name = app_name
        self.twitter_url = twitter_url
        self.mastodon_url = mastodon_url
        self.mastodon_token = mastodon_token
        self.twitter_guest_token = twitter_guest_token
        self.twitter_user_agent = twitter_user_agent
        self.strip_urls = strip_urls
        self.logger_prefix = self.app_name + " - "
        self.twitter_session_headers = {
            'Connection': 'keep-alive',
            'User-Agent': twitter_user_agent,
            'Accept': '*/*',
            'Referer': 'https://twitter.com',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br'}

    def relay(self):
        self.tweet_user_name = self.twitter_url.split(
            "twitter.com/")[-1].split("/")[0]

        logger.info(
            self.logger_prefix +
            "Reposting " +
            self.twitter_url +
            " to " +
            self.mastodon_url +
            ".")

        session = requests.Session()
        response = session.get(
            'https://twitter.com/',
            headers=self.twitter_session_headers)

        self.twitter_session_headers['authorization'] = 'Bearer ' + \
            self.twitter_guest_token
        self.twitter_session_headers['content-type'] = 'application/x-www-form-urlencoded'

        response = session.post(
            'https://api.twitter.com/1.1/guest/activate.json',
            headers=self.twitter_session_headers)

        gt = json.loads(response.text)['guest_token']
        self.twitter_session_headers['x-guest-token'] = gt

        session.cookies['gt'] = gt
        session.cookies['ct0'] = ''.join(
            random.choice(
                string.ascii_lowercase +
                string.digits) for _ in range(32))

        self.twitter_session_headers['content-type'] = 'application/json'
        self.twitter_session_headers['Referer'] = 'https://twitter.com/'

        self.graphql_params['focalTweetId'] = self.twitter_url.split(
            "/")[-1].split("?")[0]
        params_json = json.dumps(self.graphql_params)

        resp = session.get(
            f'https://twitter.com/i/api/graphql/s2RO46g9Rhw53GX2BEMfiA/TweetDetail?variables={params_json}',
            headers=self.twitter_session_headers)
        resp = json.loads(resp.text)

        tweet = resp['data']['threaded_conversation_with_injections']['instructions'][
            0]['entries'][0]['content']['itemContent']['tweet_results']['result']['legacy']

        tweet_text = self.get_tweet_text(tweet)
        tweet_text = html.unescape(tweet_text)
        tweet_text = self.escape_usernames(tweet_text)
        tweet_text = self.expand_urls(tweet, tweet_text)

        if self.strip_urls:
            tweet_text = self.remove_urls(tweet_text)

        tweet_media = self.get_tweet_media(tweet)

        # Only initialize the Mastodon API if we find something
        mastodon_api = Mastodon(
            access_token=self.mastodon_token,
            api_base_url=self.mastodon_url
        )

        media_ids = []
        for media in tweet_media:
            media_id = self.transfer_media(media, mastodon_api)
            if (media_id != -1):
                media_ids.append(media_id)
        post_id = -1
        post_id = self.post_tweet(media_ids, tweet_text, mastodon_api)
        if (post_id != -1):
            logger.info(
                self.logger_prefix +
                "Tweet posted to " +
                self.mastodon_url +
                " successfully!")
        else:
            logger.error(
                self.logger_prefix +
                "Failed to post Tweet to " +
                self.mastodon_url +
                "!")

    def get_tweet_entities(self, tweet, get_ext=True):
        entities = None

        if get_ext and 'extended_entities' in tweet:
            entities = tweet['extended_entities']
        elif 'entities' in tweet:
            entities = tweet['entities']

        return entities

    def get_tweet_media(self, tweet):
        media_list = []
        entities = self.get_tweet_entities(tweet)

        if entities is None:
            return media_list

        if 'media' in entities:
            for media in entities['media']:
                if media['type'] == 'video' or media['type'] == 'animated_gif':
                    media_list.append(
                        self.get_best_media(
                            media['video_info']['variants']))
                    break
                else:
                    media_list.append(media['media_url_https'])

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

    def get_tweet_text(self, tweet):
        text = ""
        remove_media_url = ""
        entities = self.get_tweet_entities(tweet)

        if hasattr(tweet, 'full_text'):
            text = tweet.full_text
        elif hasattr(tweet, 'text'):
            text = tweet.text

        text = "RT @" + self.tweet_user_name + ": " + text

        if 'media' in entities:
            remove_media_url = entities['media'][0]['url']

        return text.replace(remove_media_url, "")

    def expand_urls(self, tweet, tweet_text):
        text = tweet_text
        entities = self.get_tweet_entities(tweet, False)

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
        file_extension = mimetypes.guess_extension(
            media_file.headers['Content-type'])
        upload_file_name = temp_file.name + file_extension
        os.rename(temp_file.name, upload_file_name)
        temp_file_read = open(upload_file_name, 'rb')

        logger.info(
            self.logger_prefix +
            "Uploading " +
            media_url +
            " to " +
            self.mastodon_url)

        media_id = mastodon_api.media_post(upload_file_name)["id"]

        temp_file_read.close()
        os.unlink(upload_file_name)

        return media_id

    def post_tweet(self, media_ids, tweet_text, mastodon_api):
        post = mastodon_api.status_post(
            status=tweet_text,
            media_ids=media_ids,
            visibility="public",
            sensitive=False,
            spoiler_text=None,
            in_reply_to_id=None
        )

        return post["id"]

    def remove_urls(self, text):
        text = re.sub(self.remove_url_re, '', text, flags=re.MULTILINE)
        return text

    def escape_usernames(self, text):
        ats = re.findall(self.twitter_username_re, text)
        for at in ats:
            text = text.replace("@" + at, "@*" + at)

        return text
