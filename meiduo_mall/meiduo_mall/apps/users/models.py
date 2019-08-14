from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

from . import constants

# Create your models here.


class User(AbstractUser):
    """
    用户信息
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def generate_send_sms_token(self):
        """
        生成发送短信验证码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SEND_SMS_TOKEN_EXPIRES)
        data = {'mobile': self.mobile}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_send_sms_token(access_token):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SEND_SMS_TOKEN_EXPIRES)
        try:
            payload = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return payload.get('mobile')

    def generate_set_password_token(self):
        """
        生成修改密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {'user_id': self.id}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(user_id, access_token):
        """
        检验设置密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            payload = serializer.loads(access_token)
        except BadData:
            return False
        else:
            if user_id != str(payload.get('user_id')):
                return False
            else:
                return True