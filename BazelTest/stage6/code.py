

class ManagerError(Exception):
    pass


class RpcClientError(ManagerError):
    def __init__(self, error_code):
        super().__init__(self)
        self.error_dic = {
            "1000": "Client rpc server error. ",
        }

        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = self.error_code

    def __str__(self):
        return self.error_msg


class BaseError(Exception):
    def __init__(self, error_code):
        super().__init__(self)
        self.error_dic = {
            '1001': 'Get params failed. ',
            '1002': 'Type of input error. ',
        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = self.error_code

    def __str__(self):
        return self.error_msg


class AuthError(Exception):
    def __init__(self, error_code):
        super().__init__(self)
        self.error_dic = {
            '1001': '用户已存在',
            '1002': "用户不存在",
            '1003': 'register failed',
            '1004': '密码错误',
            '1005': '密码格式错误',
            '1006': 'verify code does not exists or already expired or already used.',
            '1007': 'The verify code sent failed. ',
            '1008': 'Get phone number failed',
            '1009': '手机号错误',
            '1010': '邮箱格式错误',
            '1011': '旧密码格式错误',
            '1012': '旧密码错误',
            "1013": '用户未绑定公司',
            "1014": '已指定相同权限, 请勿重复设置',
            '1016': '请检查用户名',
            '1017': '用户未指定真实用户名',
        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = self.error_code

    def __str__(self):
        return self.error_msg


class DBError(Exception):
    def __init__(self, error_code, error_message=None):
        super().__init__(self)
        self.error_dic = {
            '4001': 'Failed to count the number of times. ',
            '4002': 'Add new item failed. ',
            '4003': 'Item has already exists. ',
            '4004': 'Item does not exists. ',
            '4005': 'Get object failed',
            "4006": 'Permission error, no permission to delete file. ',
            "4007": 'Delete file error',

        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = error_message

    def __str__(self):
        return self.error_msg


class TokenError(Exception):
    def __init__(self, error_code, error_message=None):
        super().__init__(self)
        self.error_dic = {
            '5000': 'Get token failed. ',
            '5001': 'Token has already expired. ',
            '5002': 'Illegal Ip. ',
            '5003': 'Token does not exist. ',
            '5005': 'token does not match the user. ',
            "5006": 'Current user is not admin. ',
            "5007": 'Token format error.',
            "5008": '当前用户权限不足，请联系管理员提升权限',
            "5009": '[Warn]: 当前用户非管理员/文件所有者，无权限删除文件',
        }
        self.error_code = error_code
        if self.error_code in self.error_dic:
            self.error_msg = self.error_dic.get(self.error_code)
        else:
            self.error_msg = error_message

    def __str__(self):
        return self.error_msg
