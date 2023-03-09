import io
import requests
from info import *
from twifunc import *
from chatgpt import chat
# from caption import get_caption
from capcli import get_caption
from session import twi_db, logger, twi_cli


def sync_mentions():
    replied = False
    tweets = get_mentions(twi_db.last_id)
    if not tweets:
        return logger.debug('No new mentions.')

    # tweets = list(reversed(tweets))  # sort by oldest first
    tweets.sort(key=lambda x: x.id, reverse=False)  # sort by oldest first
    for tweet in tweets:
        # check permissions first
        if should_reply(tweet):
            twi_cli.like(tweet.id)
            # 回复之前先点赞
            # 是网络生活最基本的礼仪！

            process_mentions(tweet.id)
            replied = True
        # else:
        #     twi.update_status(
        #         status=not_auth,
        #         in_reply_to_status_id=tweet.id,
        #         auto_populate_reply_metadata=True
        #     )

    # update last mentioned id
    twi_db.write_last_id(tweets[-1].id)
    logger.info('Synced mentions. Last mentioned id: {}'.format(twi_db.last_id))
    return replied


def check_permission(user_id):
    return user_id in twi_db.auth_users


def should_reply(tweet):
    if not check_permission(tweet.user.id):
        return False

    # if not a reply
    if not tweet.in_reply_to_status_id:
        return True

    # if is new mention
    replied_to = get_tweet(tweet.in_reply_to_status_id)
    if bot_username in [i['screen_name'] for i in replied_to.entities['user_mentions']]:
        return False

    return True


def process_mentions(tweet_id):
    try:
        # get the whole thread
        thread = get_thread_tweets(tweet_id)
        thread_summaries = thread_to_summary(thread)
        gpt_reply = chat(thread_summaries)
        reply = tweet_cut(gpt_reply)

        return twi.update_status(
            status=reply,
            in_reply_to_status_id=tweet_id,
            auto_populate_reply_metadata=True
        )
    except Exception as e:
        logger.error(str(e))
        try:
            return twi.update_status(
                status=error_msg,
                in_reply_to_status_id=tweet_id,
                auto_populate_reply_metadata=True
            )
        except Exception as f:
            logger.error(str(f))


def thread_to_summary(thread: list):
    summaries_list = []
    summaries = extract_thread(thread)
    # list of [username, text]
    for i in range(len(summaries)):
        summaries_list.append('{username}: {text} {caption}'.format(
            username=thread[i].user.screen_name,
            text=summaries[i][1],
            caption=image_caption(thread[i])
        ).strip())

    return summaries_list


def extract_thread(thread: list):
    # remove mentions
    summaries = []
    for tweet in thread:
        summaries.append([tweet.user.screen_name, extract_text(tweet)])

    appearances = []
    for i in range(len(summaries)):
        for user in appearances:
            summaries[i][1] = summaries[i][1].replace(f'@{user} ', '', 1)
        if i > 0:
            appearances = [j['screen_name'] for j in thread[i].entities['user_mentions']]
        appearances.append(thread[i].user.screen_name)
        appearances = list(set(appearances))

    return summaries


def extract_text(tweet):
    # extract text from tweet
    text = tweet.text

    # remove urls
    for url in tweet.entities['urls']:
        text = text.replace(url['url'], '[url]')

    # remove media
    if 'media' in tweet.entities:
        if tweet.entities['media']:
            for media in tweet.entities['media']:
                text = text.replace(media['url'], '')

    # remove mentions
    # if 'user_mentions' in tweet.entities:
    #     if tweet.entities['user_mentions']:
    #         # use regex to split mentions and text
    #         mentions_re = r'^(@\w+\s)+'
    #         text = re.split(mentions_re, text)[-1]

    if text == '':
        text = '[no text]'
    return text.strip()


def image_caption(tweet):
    if get_tweet_type(tweet) != 'photo':
        return ''

    logger.info('Tweet {} found {} photo(s).'.format(tweet.id, len(get_tweet_media(tweet, 'photo'))))
    caption_text = ''
    # get image url
    image_urls = get_tweet_media(tweet, 'photo')

    for url in image_urls:
        try:
            # load image
            image = requests.get(url).content
            # get caption
            image_caption_text = get_caption(io.BytesIO(image))
            # append caption
            logger.info('Caption for image {}: {}'.format(url, image_caption_text))
            caption_text += f'[photo: {image_caption_text}] '
        except Exception as e:
            logger.error_msg('Error getting caption for image {}: {}'.format(url, e))

    return caption_text.strip()
