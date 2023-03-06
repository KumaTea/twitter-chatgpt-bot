import openai
import tweepy
import logging
import configparser
from info import *


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


config = configparser.ConfigParser(interpolation=None)
config_file = 'config.ini'
config.read(config_file)

openai.organization = config['openai']['organization']
openai.api_key = config['openai']['api_key']
model = config['openai']['model']

auth = tweepy.OAuth1UserHandler(
    config['twitter']['api_key'],
    config['twitter']['api_sec'],
    config['twitter']['acc_tok'],
    config['twitter']['acc_sec']
)
twi = tweepy.API(auth, wait_on_rate_limit=True)

twi_cli = tweepy.Client(
    consumer_key=config['twitter']['api_key'],
    consumer_secret=config['twitter']['api_sec'],
    access_token=config['twitter']['acc_tok'],
    access_token_secret=config['twitter']['acc_sec']
)

try:
    twi._me = twi.me()  # noqa
except AttributeError:
    twi._me = twi.get_user(screen_name=bot_username)


class TwitterDB:
    # saves last tweet id, authenticated users, etc.
    def __init__(self):
        self.last_id = last_mentioned_id
        self.auth_users = []
        self.cached_tweets = {}

    def write_last_id(self, last_id):
        if last_id > self.last_id:
            self.last_id = last_id
            with open(last_id_file, 'w') as f:
                f.write(str(last_id))

        logger.info('Cached tweets: {}'.format(len(self.cached_tweets)))
        self.cached_tweets = {}


twi_db = TwitterDB()
