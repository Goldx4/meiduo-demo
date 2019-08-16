from django.conf import settings
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import logging, json

from .exceptions import QQAPIException


logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    QQ认证辅助工具类
    """
    def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE

    def get_auth_url(self):
        """
        获取qq登录的网址
        :return: url网址
        """
        params = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """
        获取access_token
        :param code: qq提供的code
        :return: access_token
        """
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)

        try:
            # 发送请求
            response = urlopen(url)
            # 读取QQ返回的响应体数据
            resp_data = response.read().decode()
            # 将返回的数据转换为字典
            resp_dict = parse_qs(resp_data)
            # 注意，此处拿出来的是个列表！！！因为它认为可能会出现同名的键。
            access_token = resp_dict.get('access_token')[0]
            if not access_token:
                logger.error('code=%s msg=%s' % (resp_dict.get('code'), resp_dict.get('msg')))
                raise QQAPIException('获取access token异常')
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access token异常')

        return access_token

    def get_open_id(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:
            response = urlopen(url)
            response_data = response.read().decode()
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取openid异常')

        openid = data.get('openid', None)
        return openid
