import re
from info import *
from custom import *
from session import model, openai, bot_username, logger


def chat(dialogue: list):
    msg = gen_thread(dialogue)
    logger.info(f'Message: {msg}')
    response = openai.ChatCompletion.create(
        model=model,
        messages=msg
    )
    reply = response["choices"][0]["message"]["content"]
    logger.info(f'Reply from ChatGPT: {reply}')
    reply = gpt_to_bot(dialogue, reply)
    return reply


def gen_thread(dialogue: list):
    thread = [{"role": "user", "content": instruction}]
    for message in dialogue:
        if message.lower().startswith(bot_username.lower()):
            thread.append({"role": "assistant", "content": bot_to_gpt(message)})
        else:
            thread.append({"role": "user", "content": bot_to_gpt(message)})
    return thread


def bot_to_gpt(message):
    # modify message from bot and pass to ChatGPT
    pattern = re.compile(bot_username, re.IGNORECASE)
    msg = pattern.sub(chatgpt_name, message)

    # slang to formal
    for slang in slangs:
        if slang in msg:
            msg = msg.replace(slang, slangs[slang])

    # nickname to username
    for username in aliases:
        for nickname in aliases[username]:
            if nickname in msg:
                # msg = msg.replace(alias, f' @{user} ')
                # msg = re.sub(rf'(?![\w@])({nickname})', rf' @{username} ', msg, flags=re.IGNORECASE)
                msg = re.sub(rf'(?<!{re_ascii})({nickname})(?!{re_ascii})', rf' @{username} ', msg, flags=re.IGNORECASE)
                # negative lookbehind
                # https://docs.python.org/3/library/re.html#:~:text=Matches%20Unicode%20word
                # replace once is enough
                break

    msg = msg.replace('  ', ' ')
    return msg.strip()


def gpt_to_bot(dialogue, reply):
    # modify answer from ChatGPT and pass to bot

    # if not message.lower().startswith('ChatGPT: '.lower()):
    #     raise Exception('Not a reply from ChatGPT')

    users = [i.split(':')[0] for i in dialogue]

    if reply.startswith('ChatGPT: '):
        reply = reply[len('ChatGPT: '):]

    # remove unnecessary mention to target user
    target_username = users[-1]
    if reply.lower().startswith(f'@{target_username} '.lower()):
        reply = reply[len(f'@{target_username} '):]

    # replace username of bot
    pattern = re.compile(chatgpt_name, re.IGNORECASE)
    reply = pattern.sub(bot_username, reply)

    # recover mentions
    for username in users:
        if username in reply and f'@{username}' not in reply:
            reply = reply.replace(username, f'@{username}')

    # no need to recover slangs

    # recover nicknames to avoid unnecessary mentions
    for username in aliases:
        if f'@{username}' in reply:
            nickname = aliases[username][0]
            reply = reply.replace(f'@{username}', nickname)
            # strip spaces
            reply = re.sub(rf'\s?{nickname}\s?', nickname, reply)

    return reply
