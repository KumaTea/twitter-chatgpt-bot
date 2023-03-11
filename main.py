import time
from startup import startup
from info import default_wait
from timeline import sync_mentions


if __name__ == '__main__':
    startup()
    wait = default_wait
    while 1:
        if wait <= 0 or wait >= 2*default_wait:
            wait = default_wait

        if sync_mentions():
            wait -= 30
            time.sleep(wait)
        else:
            wait += 30
            time.sleep(wait)
