import os
from info import *
from session import twi, twi_db, logger


def startup():
    # read last mentioned id from file
    if os.path.exists(last_id_file):
        with open(last_id_file, 'r') as f:
            # do not use `write_last_id()` to avoid writing again
            twi_db.last_id = int(f.read())
    else:
        # write defaults
        twi_db.write_last_id(last_mentioned_id)

    # add authenticated users to twi_db
    self_followers = twi.get_follower_ids(user_id=twi._me.id)
    # self_friends = twi.get_friend_ids(user_id=twi._me.id)
    kuma_friends = twi.get_friend_ids(screen_name=kuma)

    twi_db.auth_users = list(set(self_followers) | (set(kuma_friends) - {twi._me.id}))

    return logger.info('Startup complete.')
