Reposts a tweet to the fediverse

This is for a single tweet only, if you want to repost automatically from a bot use [this](https://github.com/animeavi/tweet-toot).

## How to use

First, edit **config.json** with your Twitter and fediverse API keys, then install the required python libs (only the first time you run it) and run it.

```
pip install -r requirements.txt
python run.py https://twitter.com/status/...
```

## If you wanna run it more easily just create a symlink (or alias)

```
chmod +x /path/to_tweet_fedi_reposter/run.py
sudo ln -s /path/to_tweet_fedi_reposter/run.py /usr/bin/tweetoot
````
