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
    for user in aliases:
        for nickname in aliases[user]:
            if nickname in msg:
                # msg = msg.replace(alias, f' @{user} ')
                msg = re.sub(rf'([^@])({nickname})', rf'\1 @{user} ', msg, flags=re.IGNORECASE)
                # replace once is enough
                break

    msg = msg.replace('  ', ' ')
    return msg.strip()


def gpt_to_bot(dialogue, message):
    # modify answer from ChatGPT and pass to bot

    # if not message.lower().startswith('ChatGPT: '.lower()):
    #     raise Exception('Not a reply from ChatGPT')

    if message.startswith('ChatGPT: '):
        message = message[len('ChatGPT: '):]

    # replace username of bot
    pattern = re.compile(chatgpt_name, re.IGNORECASE)
    reply = pattern.sub(bot_username, message)

    # recover mentions
    users = [i.split(':')[0] for i in dialogue]
    for user in users:
        if user in reply and f'@{user}' not in reply:
            reply = reply.replace(user, f'@{user}')

    # no need to recover slangs

    # recover nicknames to avoid unnecessary mentions
    for user in aliases:
        if f'@{user}' in reply:
            nickname = aliases[user][0]
            reply = reply.replace(f'@{user}', nickname)
            # strip spaces
            reply = re.sub(rf'\s?{nickname}\s?', nickname, reply)

    # remove unnecessary mention to target user
    target_username = users[-1]
    if reply.startswith(f'@{target_username}'):
        reply = reply[len(f'@{target_username}'):]

    return reply
