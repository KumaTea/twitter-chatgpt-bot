import re
from info import *
from session import model, openai, bot_username, logger


def bot_to_gpt(message):
    pattern = re.compile(bot_username, re.IGNORECASE)
    return pattern.sub(chatgpt_name, message)


def gpt_to_bot(message):
    pattern = re.compile(chatgpt_name, re.IGNORECASE)
    return pattern.sub(bot_username, message)


def gen_thread(dialogue: list):
    thread = [{"role": "user", "content": instruction}]
    for message in dialogue:
        if message.lower().startswith(bot_username.lower()):
            thread.append({"role": "assistant", "content": bot_to_gpt(message)})
        else:
            thread.append({"role": "user", "content": bot_to_gpt(message)})
    return thread


def process_reply(dialogue, message):
    # if not message.lower().startswith('ChatGPT: '.lower()):
    #     raise Exception('Not a reply from ChatGPT')

    if message.startswith('ChatGPT: '):
        message = message[len('ChatGPT: '):]
    reply = gpt_to_bot(message)
    users = [i.split(':')[0] for i in dialogue]
    for user in users:
        if user in reply and f'@{user}' not in reply:
            reply = reply.replace(user, f'@{user}')
    return reply[:140]


def chat(dialogue: list):
    msg = gen_thread(dialogue)
    logger.info(f'Message: {msg}')
    response = openai.ChatCompletion.create(
        model=model,
        messages=msg
    )
    reply = response["choices"][0]["message"]["content"]
    logger.info(f'Reply from ChatGPT: {reply}')
    reply = process_reply(dialogue, reply)
    return reply
