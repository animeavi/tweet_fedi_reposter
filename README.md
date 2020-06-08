# Tweet-Toot
Tweet-Toot is a small Python3 project to convert a tweet to a toot.

It's basically a Twitter relay for Mastodon :)
 
Just clone it, configure it, schedule it, and it will toot new tweets at a Mastodon of your choice.

---

## How do I install this?
Getting Tweet-Toot working is pretty easy. Before you can install it, you're going to need to do the following:

- Pick a Mastodon instance of your choice. You'll need this instance's URL.
- Create an app on this Mastodon instance and generate an access token.
- Get the Twitter URL of the account you want to watch.

Once you have the above, just follow these steps:

1. Clone this repository.
2. Install the Python3 libraries by running these commands:

 - `python3 -m venv venv`
 - `source venv/bin/activate`
 - `pip3 install -r tweet-toot/requirements.txt`

3. In `config.json`, update the following:

- `TT_SOURCE_TWITTER_URL`: The Twitter account URL. Separate multiple value with `,`.
- `TT_HOST_INSTANCE`: The Mastodon instance URL. Separate multiple value with `,`.
- `TT_APP_SECURE_TOKEN`: The Mastodon app access token. Separate multiple value with `,`.
- `TT_CACHE_PATH`: Cache path. This is where we keep the last tweet, so keep this fixed.
- `TT_MODE`: Mode for Tweet-Toot when multiple Twitter or Mastodon URLs are provided. See details below.

For example:

- `TT_SOURCE_TWITTER_URL` = https://mobile.twitter.com/internetofshit
- `TT_HOST_INSTANCE` = https://botsin.space
- `TT_APP_SECURE_TOKEN` = XXXXX-XXXXX-XXXXX-XXXXX-XXXXX'
- `TT_CACHE_PATH` = `/tmp`

---

## How do I run it?
Once it's all setup, execute the app by running:

```bash
source venv/bin/activate
cd tweet-toot
python run.py
```

If all goes well, you'll see something like this:
```bash
2020-06-08 12:51:38,266 - __main__ - INFO - __main__ => Mode: one-to-one
2020-06-08 12:51:38,266 - tweettoot - INFO - relay() => Init relay from https://mobile.twitter.com/internetofshit to https://botsin.space. State file /tmp/tt_c13170b9771b0ab9736b1c2680a209347c65805c
2020-06-08 12:51:39,206 - tweettoot - INFO - get_tweets() => Fetched 20 tweets for https://mobile.twitter.com/internetofshit.
2020-06-08 12:51:39,208 - tweettoot - INFO - relay() => Tweeting 1266034895752777738 to https://botsin.space
2020-06-08 12:51:40,134 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1266034895752777738 to https://botsin.space.
2020-06-08 12:51:40,135 - tweettoot - INFO - relay() => Tweeting 1265701098934984707 to https://botsin.space
2020-06-08 12:51:41,116 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1265701098934984707 to https://botsin.space.
2020-06-08 12:51:41,117 - tweettoot - INFO - relay() => Tweeting 1265046939235729408 to https://botsin.space
2020-06-08 12:51:42,019 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1265046939235729408 to https://botsin.space.
2020-06-08 12:51:42,020 - tweettoot - INFO - relay() => Tweeting 1265046671836286977 to https://botsin.space
2020-06-08 12:51:42,936 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1265046671836286977 to https://botsin.space.
2020-06-08 12:51:42,936 - tweettoot - INFO - relay() => Tweeting 1265025125688193024 to https://botsin.space
2020-06-08 12:51:43,912 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1265025125688193024 to https://botsin.space.
2020-06-08 12:51:43,913 - tweettoot - INFO - relay() => Tweeting 1265002282627850240 to https://botsin.space
2020-06-08 12:51:44,850 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1265002282627850240 to https://botsin.space.
2020-06-08 12:51:44,851 - tweettoot - INFO - relay() => Tweeting 1263957702067261445 to https://botsin.space
2020-06-08 12:51:45,770 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263957702067261445 to https://botsin.space.
2020-06-08 12:51:45,771 - tweettoot - INFO - relay() => Tweeting 1263670113481428992 to https://botsin.space
2020-06-08 12:51:46,719 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263670113481428992 to https://botsin.space.
2020-06-08 12:51:46,720 - tweettoot - INFO - relay() => Tweeting 1263670025455624195 to https://botsin.space
2020-06-08 12:51:47,670 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263670025455624195 to https://botsin.space.
2020-06-08 12:51:47,671 - tweettoot - INFO - relay() => Tweeting 1263669246799872000 to https://botsin.space
2020-06-08 12:51:48,624 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263669246799872000 to https://botsin.space.
2020-06-08 12:51:48,625 - tweettoot - INFO - relay() => Tweeting 1263668972978933768 to https://botsin.space
2020-06-08 12:51:49,548 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263668972978933768 to https://botsin.space.
2020-06-08 12:51:49,549 - tweettoot - INFO - relay() => Tweeting 1263668670070390784 to https://botsin.space
2020-06-08 12:51:50,473 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263668670070390784 to https://botsin.space.
2020-06-08 12:51:50,474 - tweettoot - INFO - relay() => Tweeting 1263474205502423043 to https://botsin.space
2020-06-08 12:51:51,406 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263474205502423043 to https://botsin.space.
2020-06-08 12:51:51,407 - tweettoot - INFO - relay() => Tweeting 1263323591745159168 to https://botsin.space
2020-06-08 12:51:52,347 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263323591745159168 to https://botsin.space.
2020-06-08 12:51:52,347 - tweettoot - INFO - relay() => Tweeting 1263323511390642178 to https://botsin.space
2020-06-08 12:51:53,376 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263323511390642178 to https://botsin.space.
2020-06-08 12:51:53,376 - tweettoot - INFO - relay() => Tweeting 1263203533593219077 to https://botsin.space
2020-06-08 12:51:54,328 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263203533593219077 to https://botsin.space.
2020-06-08 12:51:54,329 - tweettoot - INFO - relay() => Tweeting 1263141848517881856 to https://botsin.space
2020-06-08 12:51:55,384 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263141848517881856 to https://botsin.space.
2020-06-08 12:51:55,384 - tweettoot - INFO - relay() => Tweeting 1263140615535108107 to https://botsin.space
2020-06-08 12:51:56,338 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1263140615535108107 to https://botsin.space.
2020-06-08 12:51:56,339 - tweettoot - INFO - relay() => Tweeting 1262970558154588160 to https://botsin.space
2020-06-08 12:51:57,269 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1262970558154588160 to https://botsin.space.
2020-06-08 12:51:57,270 - tweettoot - INFO - relay() => Tweeting 1262545551737917440 to https://botsin.space
2020-06-08 12:51:58,235 - tweettoot - INFO - toot_the_tweet() => OK. Tooted 1262545551737917440 to https://botsin.space.
```

---

## How does it work?
The tutorial for this code can be found here: [Tweet-Toot: Building a bot for Mastodon using Python](https://notes.ayushsharma.in/2018/09/tweet-toot-building-a-bot-for-mastodon-using-python).

If you like the tutorial, don't forget to spread the word on Mastodon :)

---

## How do I build the Docker image and run it?
I've added a `Dockerfile` with this repo so you can get up and running with Docker quickly.

### To build the Docker image locally:

1. Clone this repo.
   
2. In the main directory, run:
   
   ```
   docker build -t tweet-toot:latest -f Dockerfile tweet-toot
   ```

3. Export your Mastodon token in your environment:
   
   ```
   export TT_APP_SECURE_TOKEN="<token>"
   ```

   We'll pass this to the container later. No need to hard-code the `config.json`.

4. Execute the container:
   
   ```
   docker run --rm -e TT_APP_SECURE_TOKEN="$TT_APP_SECURE_TOKEN" -v /tmp:/tmp tweet-toot:latest
   ```

   We need `TT_CACHE_PATH` same across `docker run`s, so we're mounting a local directory into the container's `/tmp`. Customise as you see fit.
   
   To override more config paramters, just pass more `-e`s to Docker.

---

## What's up with `TT_MODE`?
As Tweet-Toot has grown, there have been requests over the years to allow relaying many Twitter accounts to the same Mastodon instance, or relay one Twitter account to many Mastodons, etc. As you can imagine, there are 4 possible scenarios:

1. One Twitter account posts to a single Mastodon (default behaviour).
2. One Twitter account posts to many Mastodons.
3. Many Twitter accounts post to a single Mastodon.
4. Many Twitter accounts post to many Mastodons.

The way this works is this. The `TT_SOURCE_TWITTER_URL`, `TT_HOST_INSTANCE`, and `TT_APP_SECURE_TOKEN` values are split by `,`, and the rest of the processing follows the value of `TT_MODE`.

- `TT_MODE: one-to-one`: In this mode, the first Twitter URL is picked and it is relayed to the first Mastodon URL/Token combination. This repeats until we run out of Twitter URLs or Mastodon URLs. The number of Twitter accounts must be equal to the number of Mastodon URLs/tokens to avoid wierdness.

- `TT_MODE: one-to-many`: In this mode, the first Twitter URL is picked and relayed to all Mastodon instances. Then the next Twitter URL is picked. 

- `TT_MODE: many-to-one`: In this mode, every Twitter account is relayed to a single Mastodon instance.

- `TT_MODE: many-to-many`: In this mode, every Twitter account is relayed to all Mastodon instances.

Remember, the number of values in `TT_HOST_INSTANCE` and `TT_APP_SECURE_TOKEN` should always be equal so that we can pick the token for every instance.

This `,` structure is put in place so that the `config.json` values can still be specified as `env` variables.

---

## Things to remember
- The script is designed to toot once per invokation. I recommend timing your cron jobs according to the post frequency that you need instead of modifying the code.
- Mastodon instance admins are people too. Don't toot-blast your instance and make life harder for them.
- When configuring your bot, ensure you clearly display an account where you can be reached in case of issues.

Have fun :)

---

For questions or contributions, please create an issue.

You can find me on [Mastodon](https://mastodon.technology/@ayushsharma22) or [ayushsharma.in](https://ayushsharma.in).