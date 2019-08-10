from rest_framework import serializers, status

from django_redis import get_redis_connection
from redis import RedisError
import logging
from rest_framework.response import Response

logger = logging.getLogger('django')

class CheckImageCodeSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):
        """校验图片验证码是否正确"""
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 查询redis数据库，获取真实的验证码
        redis_conn = get_redis_connection('verify_codes')
        try:
            real_image_code = redis_conn.get('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)
            return Response({"message": "服务器内部错误"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 图片验证码不存在或者已过期
        if not real_image_code:
            raise serializers.ValidationError('验证码无效')

        # 删除图片验证码
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 比较图片验证码是否正确
        real_image_code = real_image_code.decode()  # 从redis中取出需要decode
        if text.lower() != real_image_code.lower():
            raise serializers.ValidationError('验证码错误')

        # redis中发送短信验证码的标识 send_flag_<mobile> : 1， 由redis维护60s的有效期
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs