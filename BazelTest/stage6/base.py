import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import base64
from tornado.web import RequestHandler

from account_utils import get_account_info, auth_login_redirect
from extensions import ModelsManager

secret_key = b'YourSecretKey'
UPLOAD_DIRECTORY = "upload"


class BaseHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

    def get_client_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        return remote_ip


class IndexHandler(BaseHandler):
    @auth_login_redirect
    def get(self):
        cookie_token = self.get_secure_cookie("token")
        token = self.get_argument("Authorization", None)
        username, account_name, is_admin = get_account_info(cookie_token, token)

        model_manager = ModelsManager()
        models_count = model_manager.get_models_count(username, is_admin=is_admin)
        model_list = model_manager.get_models(0, models_count, username, is_admin)

        self.render("index.html", username=username, account_name=account_name, is_admin=is_admin, model_list=model_list)


class UploadHandler(BaseHandler):
    def get(self):
        self.render("upload.html")

    def post(self):
        offset = int(self.get_argument('offset', 0))
        file = self.request.files['file'][0]

        file_name = file['filename']
        file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

        with open(file_path, 'ab') as f:
            f.seek(offset)
            print(file['body'])
            f.write(file['body'])

        self.write({'message': 'Chunk uploaded successfully'})
