from session import twi, twi_db, logger
from info import last_mentioned_id


def get_tweet_type(tweet):
    # text, photo, video, gif
    if getattr(tweet, 'extended_entities', None):
        if tweet.extended_entities['media'][0]['type'] == 'photo':
            return 'photo'
        elif tweet.extended_entities['media'][0]['type'] == 'video':
            return 'video'
        elif tweet.extended_entities['media'][0]['type'] == 'animated_gif':
            return 'gif'
    return 'text'


def get_tweet_media(tweet, media_type):
    if media_type == 'photo':
        return [i['media_url_https'] for i in tweet.extended_entities['media']]
    elif media_type == 'video' or media_type == 'gif':
        return tweet.extended_entities['media'][0]['video_info']['variants'][0]['url']
    else:
        return None


def get_media_entities_url(tweet):
    return tweet.entities['media'][0]['url']


def get_urls_in_tweet(tweet):
    if getattr(tweet, 'entities', None):
        if tweet.entities.get('urls', None):
            return [
                {'url': url['url'],
                 'display_url': url['display_url'],
                 'expanded_url': url['expanded_url']
                 } for url in tweet.entities['urls']
            ]
    else:
        return []


def get_thread_tweets(tweet_id):
    thread = []
    while True:
        tweet = get_tweet(tweet_id)
        thread.append(tweet)
        if tweet.in_reply_to_status_id is None:
            break
        logger.info(f'Found reply: {tweet.in_reply_to_status_id} -> {tweet.id}')
        tweet_id = tweet.in_reply_to_status_id

    thread.sort(key=lambda x: x.id, reverse=False)  # sort by oldest first
    return thread


def get_latest_tweet_id(user_id):
    return twi.user_timeline(user_id=user_id, count=1)[0].id


def get_mentions(l_id=last_mentioned_id):
    tweets = twi.mentions_timeline(
        count=200,
        since_id=l_id,
        trim_user=False,
        include_entities=True,
    )
    for i in range(len(tweets)):
        if tweets[i].truncated:
            tweets[i] = get_tweet(tweets[i].id)
        twi_db.cached_tweets[tweets[i].id] = tweets[i]
    return tweets


def get_tweet(tweet_id):
    if tweet_id in twi_db.cached_tweets:
        return twi_db.cached_tweets[tweet_id]
    else:
        tweet = twi.get_status(tweet_id, tweet_mode='extended')
        setattr(tweet, 'text', tweet.full_text)
        twi_db.cached_tweets[tweet_id] = tweet
        return tweet
