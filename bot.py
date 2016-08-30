import os
import tweepy
import json
import markovify
from secrets import *
from time import gmtime, strftime

# ====== Individual bot configuration ==========================
bot_username = '626f74'
logfile_name = bot_username + ".log"
datafile_name = bot_username + "_data.json"
whitelist_name = "whitelist.json"
corpus_name = "corpus.txt"

# ==============================================================

# Variables
count = 0
text_model = ""

# Twitter authentication
auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
own_id_str = me.id_str
own_id = me.id


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        # not me
        if status.user.id != own_id:
            # user in whitelist
            if user_authorized(status.user.id):
                if status.text.find("hello") > 7:
                    # tweet hello
                    tweet_text = create_tweet(status.user.screen_name, 0)
                    tweet(tweet_text, status.id)
                else:
                    # tweet markov
                    tweet_text = create_tweet(status.user.screen_name, 1)
                    tweet(tweet_text, status.id)
            else:
                # add user if requested
                if status.text.find("add me") > 7:
                    whitelist_user(status.user.id)

    def on_error(self, status_code):
        if status_code == 420:
            return False


def create_tweet(name, tweet_type):
    """Create the text of the tweet you want to send."""
    if tweet_type == 0:
        # tweet hello with counter because of double
        counter = get_counter()
        text = "Hello @" + name + " " + str(counter)
        set_counter(counter + 1)
    else:
        # tweet sherlock
        text = "@" + name + " " + text_model.make_short_sentence(139)

    return text


def tweet(text, tweetID=0):
    """Send out the text as a tweet."""
    # Send the tweet and log success or failure
    print("tweet ID", tweetID)
    try:
        if tweetID != 0:
            api.update_status(text, tweetID)
        else:
            api.update_status(text)
    except tweepy.error.TweepError as e:
        log(e.message)
    else:
        log("Tweeted: " + text)
        print("Tweeted")


def log(message):
    """Log message to logfile."""
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)


def get_counter():
    with open(datafile_name) as f:
        data = json.load(f)

    print('got', data['counter'])
    return data['counter']


def set_counter(i):
    with open(datafile_name) as f:
        data = json.load(f)

    data['counter'] = i
    print('set', data['counter'])

    with open(datafile_name, 'w') as f:
        json.dump(data, f)


def whitelist_user(user_id):
    with open(whitelist_name) as f:
        data = json.load(f)

    a_dict = {'id': user_id}
    data['user'].append(a_dict)
    log('Whitelisted user: ' + str(user_id))

    with open(whitelist_name, 'w') as f:
        json.dump(data, f)


def user_authorized(user_id):
    with open(whitelist_name) as f:
        data = json.load(f)

    user_in_whitelist = False

    for user in data['user']:
        if user['id'] == user_id:
            user_in_whitelist = True
            break

    return user_in_whitelist


def get_user_name(user_id):
    u = api.get_user(user_id)
    return u.screen_name


def prepare_markov():
    # raw text as string
    with open(corpus_name) as f:
        corpus = f.read()
    # build model
    global text_model
    text_model = markovify.Text(corpus, state_size=3)


if __name__ == "__main__":
    prepare_markov()

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
    myStream.filter(follow=[own_id_str])