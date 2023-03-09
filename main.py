import time
from startup import startup
from timeline import sync_mentions


if __name__ == '__main__':
    startup()
    while 1:
        if sync_mentions():
            time.sleep(60)
        else:
            time.sleep(300)

