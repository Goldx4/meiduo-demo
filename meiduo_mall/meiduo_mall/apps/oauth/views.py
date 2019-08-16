from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings

from .utils import OAuthQQ
from .models import OAuthQQUser
from .exceptions import QQAPIException

# Create your views here.


class QQAuthURLView(APIView):
    """
    获取QQ登录的url
    """
    def get(self, request):
        """
        提供用于qq登录的url
        """
        state = request.query_params.get('state')
        oauth = OAuthQQ(state=state)
        auth_url = oauth.get_auth_url()

        return Response({'auth_url': auth_url}, status=status.HTTP_200_OK)


class QQAuthUserView(APIView):
    """
    QQ登录的用户
    """
    def get(self, request):
        """
        获取qq登录的用户数据
        """
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ()
        try:
            # 凭借code从QQ服务器获取用户access_token
            access_token = oauth.get_access_token(code)
            # 凭借access_token从QQ服务器获取用户openid
            openid = oauth.get_open_id(access_token)
        except QQAPIException as e:
            return Response({'message': '获取QQ用户数据异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 根据openid 去后台查询此用户是否绑定过美多商城
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果未绑定过，生成并返回接下来的绑定手机号这一步骤所需要的 accesstoken
            access_token = OAuthQQUser.generate_save_user_token(openid)
            return Response({'access_token': access_token})
        else:
            # 如果绑定过，直接返回JWT token
            user = oauth_user.user
            # 生成记录登录状态的token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'user_id': user.id,
                'token': token,
                'username': user.username
            })





