from session import twi_db


def check_permission(user_id):
    return user_id in twi_db.auth_users
