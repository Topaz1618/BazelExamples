import re
import json
import asyncio
import random
import uuid
import hmac
import hashlib
from datetime import datetime

from base import BaseHandler
from code import AuthError, TokenError, BaseError
from config import SECRET
from extensions import UserManager
from account_utils import (create_token, remove_token, auth_login_redirect, get_token_user, admin_login_redirect,
                           get_account_info)
from log_handler import logger


class RegisterHandler(BaseHandler):
    def get(self):
        self.render('account/register.html')

    def post(self):
        try:
            username = self.get_argument('username', None)
            account_name = self.get_argument('account_name', None)
            password = self.get_argument('password', None)
            confirm_password = self.get_argument('confirm_password', None)


            if username is None or len(username) == 0:
                raise AuthError("1003")

            if len(re.findall("1[3|4|5|6|7|8|9][0-9]{9}", username)) == 0:
                raise AuthError("1009")



            if password is None or len(confirm_password) == 0:
                raise AuthError("1003")

            if password != confirm_password:
                raise AuthError("1003")

            user_manager = UserManager()
            is_exists = user_manager.is_exists(username)

            if is_exists:
                raise AuthError("1001")

            pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', password)
            if pwd_verify is None:
                raise AuthError("1005")


            password = hmac.new(SECRET, password.encode(), hashlib.md5).hexdigest()
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            user_manager.create_user(account_name, username, password, is_admin=False, created_time=upload_date)

            message = {
                'msg': 'register successful',
                'error_code': '1000'
            }
            logger.warning(f"User [{username}] Register successful")

        except AuthError as e:

            logger.error(e.error_msg)
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            logger.error(e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class LoginHandler(BaseHandler):
    def get(self):
        self.render('account/login.html')

    def post(self):
        try:
            username = self.get_argument('username', None)
            password = self.get_argument('password', None)

            if username is None or len(username) == 0:
                raise AuthError("1003")

            if password is None or len(password) == 0:
                raise AuthError("1003")

            pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', password)
            if pwd_verify is None:
                raise AuthError("1005")

            user_manager = UserManager()
            is_exists = user_manager.is_exists(username)

            print(username)

            if not is_exists:
                user_manager.close()
                raise AuthError("1002")

            user_info = user_manager.get_user(username)
            account_name = user_info.get("account_name")
            # from ipdb import set_trace; set_trace();
            password = hmac.new(SECRET, password.encode(), hashlib.md5).hexdigest()

            is_match = user_manager.check_user_password(user_info, password)
            if not is_match:
                user_manager.close()
                raise AuthError("1004")

            remote_ip = self.get_client_ip()
            user_manager.update_remote_ip(username, remote_ip)

            token = create_token(username, account_name, remote_ip)

            logger.warning(f"User [{username}] logged in successfully.")
            message = {
                'msg': {'token': token, 'username': username},
                'error_code': '1000'
            }

            self.clear_cookie("token")
            self.clear_cookie("username")
            self.set_secure_cookie("token", token, 3600)
            self.set_cookie("username", username)
            user_manager.close()

        except AuthError as e:
            logger.error(e.error_msg)
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except BaseError as e:
            logger.error(e.error_msg)

            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            logger.error(e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


class LogoutHandler(BaseHandler):
    def get(self):
        try:
            token = self.get_secure_cookie("token")
            if token is None:
                self.render("account/login.html")
                return

            if isinstance(token, bytes):
                token = token.decode()

            remove_token(token)
            self.clear_cookie("token")
            self.render("account/login.html")

        except BaseError as e:
            logger.error(e.error_msg)
            self.render("account/login.html")

        except AuthError as e:
            logger.error(e.error_msg)
            self.render("login.html")

        except TokenError as e:
            logger.error(e.error_msg)
            self.render("account/login.html")

        except Exception as e:
            logger.error(e)
            self.render("account/login.html")

    def post(self):
        try:
            token = self.get_argument("Authorization", None)

            if token is None or len(token) == 0:
                raise TokenError("5000")

            remove_token(token)
            self.clear_cookie("token")
            message = {'msg': "Logout successful. ", 'error_code': '1000'}

        except TokenError as e:
            logger.error(e.error_msg)
            message = {'msg': e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            logger.error(e)
            message = {'msg': "Logout failed", 'error_code': '1010'}

        self.write(message)


class RestPasswordView(BaseHandler):
    @auth_login_redirect
    def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)

        self.render('account/reset_password.html', username=username,  account_name=account_name, is_admin=is_admin)

    @auth_login_redirect
    def post(self):
        try:
            username = self.get_argument('username', None)
            old_password = self.get_argument('old_password', None)
            password = self.get_argument('password', None)
            confirm_password = self.get_argument('confirm_password', None)

            # print(username, old_password, password, confirm_password)

            if username is None or len(username) == 0:
                raise AuthError("1003")

            if old_password is None or len(old_password) == 0:
                raise AuthError("1003")

            if password is None or len(password) == 0:
                raise AuthError("1003")

            if password != confirm_password:
                raise AuthError("1003")

            if old_password == password:
                raise AuthError("1013")

            old_pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', old_password)
            if old_pwd_verify is None:
                raise AuthError("1011")

            pwd_verify = re.match(r'[A-Za-z0-9@#$%^&+=]{8,16}$', password)
            if pwd_verify is None:
                raise AuthError("1005")

            user_manager = UserManager()
            is_exists = user_manager.is_exists(username)

            if not is_exists:
                raise AuthError("1002")

            user_info = user_manager.get_user(username)
            old_password = hmac.new(SECRET, old_password.encode(), hashlib.md5).hexdigest()
            password = hmac.new(SECRET, password.encode(), hashlib.md5).hexdigest()

            # print("old pass:", old_password, password)
            is_match = user_manager.check_user_password(user_info, old_password)

            if not is_match:
                user_manager.close()
                raise AuthError("1012")

            user_manager.update_password(username, password)
            logger.warning(f"User {username} updated password successfully.")

            message = {
                'msg': {"user": username,},
                'error_code': '1000',

            }
        except BaseError as e:
            logger.error(e.error_msg)
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except AuthError as e:
            logger.error(e.error_msg)
            message = {'msg':  e.error_msg, 'error_code': e.error_code}

        except Exception as e:
            logger.error(e)
            message = {'msg': "Unknown Error", 'error_code': '1010'}

        self.write(message)


