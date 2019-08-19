from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from . import serializers
from .models import User

# Create your views here.


class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserView(CreateAPIView):
    """
    用户信息
    """
    serializer_class = serializers.CreateUserSerializer


class PasswordTokenView(GenericAPIView):
    """
    用户帐号设置密码的token
    """
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成修改用户密码的access token
        access_token = user.generate_set_password_token()

        return Response({'user_id': user.id, 'access_token': access_token})


class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    """
    用户密码
    """
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, pk):
        return self.update(request, pk)


class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailView(CreateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]

    # 为了使视图的create方法在对序列化器进行save操作时执行序列化器的update方法，更新user的email属性
    # 所以重写get_serializer方法，在构造序列化器时将请求的user对象传入
    # 注意：在视图中，可以通过视图对象self中的request属性获取请求对象
    def get_serializer(self, *args, **kwargs):
        return serializers.EmailSerializer(self.request.user, self.request.data)


class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.check_verify_email_token(token)
        if not user:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})