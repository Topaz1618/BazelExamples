import base64
import uuid
import jwt

from time import time, mktime, strptime
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


from config import SECRET_KEY, TOKEN_TIMEOUT
from code import TokenError, AuthError
from mongodb_models import conn_db
from enums import UserLevel
from extensions import UserManager


def get_account_info(cookie_token, token):
    username, account_name = get_token_user(cookie_token, token)

    user_manager = UserManager()
    is_admin = user_manager.check_is_admin(username)
    user_manager.close()

    return username, account_name, is_admin


def load_key_from_file():
    """
    Load the encryption key from a file.
    """
    with open('data.ini', 'rb') as file:
        data = file.read()
    return data


def generate_temporary_key():
    """
      Generate a temporary encryption key.
    """
    random_uuid = uuid.uuid4()
    key = str(random_uuid)[:16]
    return key


def base64_encode(data):
    """
    Encode data using Base64.
    """
    encoded_bytes = base64.b64encode(data)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string



def generate_gridfs_filename(filename, username):
    """
    Generate a GridFS filename for storing files.
    """
    gridfs_filename = f"{username}_{filename}"
    return gridfs_filename


def generate_record_filename(filename, username, timestamp):
    """
    Generate a filename for recording files with a timestamp.
    """
    record_filename = f"{username}_{timestamp}_{filename}"
    return record_filename


def timestamp_to_date_string(timestamp):
    """
    Convert a timestamp to a date string.
    """
    date_string = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return date_string


def timestamp_to_date_time(timestamp):
    """
    Convert a timestamp to a datetime object with adjusted time zone.
    """
    date_time = datetime.utcfromtimestamp(timestamp) + timedelta(hours=8)
    return date_time


def check_file_length(file_info):
    """
    Calculate the total length of files in a list of documents.
    """
    uploaded_size = 0
    for document in file_info:
        uploaded_size += document["length"]
    return uploaded_size


def create_token(user, account_name, remote_ip=None):
    """
    Create a JWT token for authentication.
    """
    payload = {
        "timestamp": time(),
        "account_name": account_name,
        "username": user,
        "remote_ip": remote_ip,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token.decode()


def remove_token(token):
    """
    Removes Token from session and checks its validity.
    """
    try:
        # Decode the token to extract user information
        token_dic = jwt.decode(token.encode(), SECRET_KEY)
        username = token_dic.get('username')
        token_ip = token_dic.get('remote_ip')

    except Exception as e:
        raise TokenError("5004")

    # Connect to the database and check user's existence and remote IP match
    client, db = conn_db()
    users_collection = db['Users']
    user = users_collection.find_one({'username': username})

    if not user:
        client.close()
        raise TokenError("5003")

    if user.get("last_remote_ip") != token_ip:
        client.close()
        raise TokenError("5002")

    client.close()


def common_token_verification(remote_ip, token, is_admin=False, is_reviewer=False):
    """
     Common Token Verification for various authentication scenarios.


     Provides a common method to verify tokens in various authentication scenarios.
     It decodes the token, extracts user information, and performs various checks:
        - token timeout
        - IP consistency
        - user

    It also validates user existence and IP consistency in the database.
    """
    token_dic = jwt.decode(token.encode(), SECRET_KEY)
    username = token_dic.get('username')
    token_ip = token_dic.get('remote_ip')

    current_time = time()
    if current_time - token_dic['timestamp'] > TOKEN_TIMEOUT:
        raise TokenError("5001")

    if remote_ip != token_ip:
        raise TokenError("5002")

    client, db = conn_db()
    users_collection = db['AIUsers']
    user_obj = users_collection.find_one({'username': username})

    print(token_dic, remote_ip, current_time, )
    if not user_obj:
        client.close()
        raise TokenError("5003")

    if is_admin:
        if user_obj.get("is_admin") != UserLevel.ADMIN.value:
            client.close()
            raise TokenError("5008")

    if user_obj.get("last_remote_ip") != token_ip:
        client.close()
        raise TokenError("5002")

    return username


def token_verification(remote_ip, token, is_admin=False):
    common_token_verification(remote_ip, token, is_admin)
    return True


def inner_function(self, func, is_admin,  *args, **kwargs):
    token = self.get_argument("Authorization", None)

    cookie_token = self.get_secure_cookie("token")

    try:
        if not token:
            if cookie_token is not None:
                print("Use cookie token")
                token = cookie_token

            else:
                raise TokenError("5000")

        if isinstance(token, bytes):
            token = token.decode()

        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        username = token_verification(remote_ip, token, is_admin)

    except TokenError as e:

        self.render("account/authority_error.html", error_message=e.error_msg, error_code=e.error_code)
        return

    except AuthError as e:
        return

    except Exception as e:
        print("Auth token exception >>>> ", e)
        self.render("account/login.html")
        return

    func(self, *args, **kwargs)


async def async_inner_function(self, func, is_admin, *args, **kwargs):
    token = self.get_argument("Authorization", None)

    cookie_token = self.get_secure_cookie("token")

    try:
        if not token:
            if cookie_token is not None:
                token = cookie_token

            else:
                raise TokenError("5000")

        if isinstance(token, bytes):
            token = token.decode()

        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        username = token_verification(remote_ip, token, is_admin)

    except TokenError as e:
        self.render("account/authority_error.html", error_message=e.error_msg, error_code=e.error_code)
        return

    except AuthError as e:
        return

    except Exception as e:
        print("Auth token exception >>>> ", e)
        self.render("account/login.html")
        return

    await func(self, *args, **kwargs)


def auth_login_redirect(func):
    """
    Authentication and Login Redirect Decorator for general users

    Handles authentication and login redirection for general users.
    It uses the token_verification function to verify tokens.
    It extracts and decodes tokens from cookies or headers and performs various checks.
    It handles token-related errors and renders appropriate error pages.

    """

    def inner(self, *args, **kwargs):
        is_admin = False
        inner_function(self, func, is_admin, *args, **kwargs)

    return inner


def admin_login_redirect(func):
    """
        Authentication and Login Redirect Decorator for admin users

        The admin_login_redirect decorator handles authentication and login redirection specifically for administrators.
        It utilizes the token_verification function with the is_admin parameter set to True to verify tokens.
        Similar to auth_login_redirect, it handles token-related errors and renders appropriate error pages.

    """

    def inner(self, *args, **kwargs):
        is_admin = True
        inner_function(self, func, is_admin,  *args, **kwargs)

    return inner


def async_admin_login_redirect(func):
    """
        Authentication and Login Redirect Decorator for admin users

        The admin_login_redirect decorator handles authentication and login redirection specifically for administrators.
        It utilizes the token_verification function with the is_admin parameter set to True to verify tokens.
        Similar to auth_login_redirect, it handles token-related errors and renders appropriate error pages.

    """
    async def inner(self, *args, **kwargs):
        is_admin = True
        await async_inner_function(self, func, is_admin, *args, **kwargs)

    return inner


def async_admin_login_redirect(func):
    """
        Authentication and Login Redirect Decorator for admin users

        The admin_login_redirect decorator handles authentication and login redirection specifically for administrators.
        It utilizes the token_verification function with the is_admin parameter set to True to verify tokens.
        Similar to auth_login_redirect, it handles token-related errors and renders appropriate error pages.

    """

    async def inner(self, *args, **kwargs):
        is_admin = True
        await async_inner_function(self, func, is_admin, *args, **kwargs)

    return inner


def async_auth_login_redirect(func):
    """
        Authentication and Login Redirect Decorator for admin users

        The admin_login_redirect decorator handles authentication and login redirection specifically for administrators.
        It utilizes the token_verification function with the is_admin parameter set to True to verify tokens.
        Similar to auth_login_redirect, it handles token-related errors and renders appropriate error pages.

    """

    async def inner(self, *args, **kwargs):
        is_admin = False
        await async_inner_function(self, func, is_admin, *args, **kwargs)

    return inner


def get_token_user(cookie_token, token):
    """
    Validate the current logged-in user.
    """
    if token is None or len(token) == 0:
        if cookie_token is None:
            raise TokenError("5000")
        else:
            print("use cookie token")
            token = cookie_token

    if isinstance(token, bytes):
        token = token.decode()

    token_dic = jwt.decode(token.encode(), SECRET_KEY)
    username = token_dic.get('username')
    account_name = token_dic.get('account_name')
    print(f">> Current User: {username}")
    return username, account_name




def add_num(x, y):
    return x + y


def subtract_num(x, y):
    return x - y


def generate_page_list(current_page, total_pages):
    """
    Generate a list of pages for pagination.
    """

    page_list = []

    if total_pages <= 5:
        page_list = list(range(1, total_pages + 1))
    else:
        if current_page <= 3:
            page_list = [1, 2, 3, 4, 5]
        elif current_page >= total_pages - 2:
            page_list = [total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
        else:
            page_list = [current_page - 2, current_page - 1, current_page, current_page + 1, current_page + 2]
    return page_list


if __name__ == "__main__":
    token = create_token("15600803270", "127.0.0.1")
    print(token)