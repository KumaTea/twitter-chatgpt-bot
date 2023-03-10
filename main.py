import time
from startup import startup
from timeline import sync_mentions


if __name__ == '__main__':
    startup()
    wait = 60
    while 1:
        if wait <= 0:
            wait = 60

        if sync_mentions():
            wait -= 30
            time.sleep(wait)
        else:
            wait += 30
            time.sleep(wait)
