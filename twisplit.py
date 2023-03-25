import re
from session import logger
from info import bot_username


def tweet_len(text):
    ascii_range = range(0, 127)
    index = 0
    count = 0
    for i in text:
        index += 1
        if ord(i) in ascii_range:
            count += 1
        else:
            count += 2
    return count


def tweet_cut(text):
    """
    Twitter only allows 280 characters in a tweet.
    However Chinese and Japanese characters are counted as 2 characters.
    """
    max_tweet_length = 280
    ascii_range = range(0, 127)

    if len(text) <= max_tweet_length/2:
        return text

    index = 0
    count = 0
    for i in text:
        index += 1
        if ord(i) in ascii_range:
            count += 1
        else:
            count += 2

        if count == max_tweet_length:  # 280
            return text[:index-2] + '…'
        elif count > max_tweet_length:  # 281
            return text[:index-3] + '…'

    return text


def tweet_split(text):
    """
    Split tweet into multiple tweets if exceeds 280 characters.
    Add "(1/n)" to the end of each tweet.
    Add "……" if the tweet is not the end.
    """
    max_tweet_length = 280
    ascii_range = range(0, 127)

    if tweet_len(text) <= max_tweet_length:
        return [text]

    logger.info('Tweet is too long, splitting...')
    tweets = []
    index = 0
    count = 0
    for i in text:
        index += 1
        if ord(i) in ascii_range:
            count += 1
        else:
            count += 2

        if count + 2 + len(f'…… (i/nn)') >= max_tweet_length:
            tweets.append(text[:index] + f'…… ({len(tweets)+1}/TOTAL_COUNT_PLACEHOLDER)')
            text = text[index:]
            index = 0
            count = 0

    tweets.append(text + f' ({len(tweets)+1}/TOTAL_COUNT_PLACEHOLDER)')

    for i in range(len(tweets)):
        tweets[i] = tweets[i].replace('TOTAL_COUNT_PLACEHOLDER', str(len(tweets)))

    return tweets


def tweet_split_no_break(text):
    max_tweet_length = 280
    ascii_range = range(0, 127)

    if tweet_len(text) <= max_tweet_length:
        return [text]

    logger.info('Tweet is too long, splitting...')
    tweets = []
    count = 0
    tweet = ''
    buffer = ''
    for i in text:
        if ord(i) in ascii_range:
            count += 1
            if i == ' ':
                tweet += buffer + i
                buffer = ''
            else:
                buffer += i
        else:
            count += 2
            tweet += buffer + i
            buffer = ''

        if count + len(buffer) + 2 + len(f'…… (i/nn)') >= max_tweet_length:
            tweets.append(tweet.strip() + f'…… ({len(tweets)+1}/TOTAL_COUNT_PLACEHOLDER)')
            tweet = buffer
            buffer = ''
            count = len(tweet)

    tweets.append((tweet + buffer).strip() + f' ({len(tweets)+1}/TOTAL_COUNT_PLACEHOLDER)')

    for i in range(len(tweets)):
        tweets[i] = tweets[i].replace('TOTAL_COUNT_PLACEHOLDER', str(len(tweets)))

    return tweets


def merge_split(tweet_list: list):
    merged_list = []
    to_merge = ''
    for tweet in tweet_list:
        # 'username: text'
        if tweet.startswith(f'{bot_username}: '):
            # if tweet.endswith(')'):  # …… (i/nn)
            if re.findall(r'\(\d+\/\d+\)', tweet):  # …… (i/nn)
                if '…… (' in tweet:
                    # uncomplete split
                    to_merge += tweet[len(f'{bot_username}: '):tweet.rfind('…… (')]
                    if ord(to_merge[-1]) < 128:
                        # last char is ascii
                        to_merge += ' '
                else:
                    # last split
                    to_merge += tweet[len(f'{bot_username}: '):tweet.rfind(' (')]
                    merged_list.append(f'{bot_username}: ' + to_merge)
                    to_merge = ''
            else:
                # bot, but not split
                if to_merge:
                    merged_list.append(f'{bot_username}: ' + to_merge)
                    to_merge = ''
                merged_list.append(tweet)
        else:
            # not bot
            if to_merge:
                merged_list.append(f'{bot_username}: ' + to_merge)
                to_merge = ''
            merged_list.append(tweet)
    if to_merge:
        merged_list.append(f'{bot_username}: ' + to_merge)

    return merged_list
