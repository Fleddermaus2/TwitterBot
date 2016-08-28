import os
import tweepy
import json
from secrets import *
from time import gmtime, strftime

# ====== Individual bot configuration ==========================
bot_username = '626f74'
logfile_name = bot_username + ".log"
datafile_name = bot_username + "_data.json"
whitelist_name = "whitelist.json"

# ==============================================================

# Variables
count = 0

# Twitter authentication
auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()
own_id_str = me.id_str
own_id = me.id


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.id != own_id:
            if user_authorized(status.user.id):
                if status.text.find("hello") > 7:
                    tweet_text = create_tweet(status.user.screen_name)
                    tweet(tweet_text, status.id)
            else:
                if status.text.find("add me") > 7:
                    whitelist_user(status.user.id)
        else:
            print('own post, ignore them')

    def on_error(self, status_code):
        if status_code == 420:
            return False


def create_tweet(name):
    """Create the text of the tweet you want to send."""
    # Replace this with your code!
    counter = get_counter()
    text = "Hello @" + name + " " + str(counter)
    set_counter(counter + 1)
    return text


def tweet(text, tweetID = 0):
    """Send out the text as a tweet."""
    # Send the tweet and log success or failure
    try:
        if tweetID != 0:
            api.update_status(text, tweetID)
        else:
            api.update_status(text)
    except tweepy.error.TweepError as e:
        log(e.message)
    else:
        log("Tweeted: " + text)


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

if __name__ == "__main__":

    """tweet_text = create_tweet()
    tweet(tweet_text)"""

    """for status in tweepy.Cursor(api.mentions_timeline).items(10):
        print(count, ":", status.text)
        count += 1"""

    print('start stream listener')
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
    myStream.filter(follow=[own_id_str])
