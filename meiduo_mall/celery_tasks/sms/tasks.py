import logging
from celery_tasks.main import app
from .yuntongxun.sms import CCP
from . import constants

logger = logging.getLogger('django')


@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码
    :param mobile: 手机号
    :param sms_code: 验证码
    :return: 
    """

    # 发送短信
    try:
        ccp = CCP()
        sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        result = ccp.send_template_sms(mobile, [sms_code, sms_code_expires], constants.SMS_CODE_TEMP_ID)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)