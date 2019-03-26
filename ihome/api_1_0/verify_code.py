# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants, db
from ihome.models import User
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.libs.yuntongxun.SendTemplateSMS import CCP
import random


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码编号
    :return:
    """
    # 名字，真实文本，图片数据
    name, text, image_data = captcha.generate_captcha()

    # redis_store.set("image_code_%s" % image_code_id, text)
    # redis_store.expire("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 获取异常，记录到日志文件
        current_app.logger.error(e)
        # 返回json数据类型
        return jsonify(errno=RET.DBERR, errmsg=u"保存图片验证码失败")

    # 返回图片数据
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    if not all([image_code, image_code_id]):
        # 参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg=u"参数不完整")

    # 取出图片验证码的真实文本
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"redis数据库异常")

    # 判断图片验证码是否过期
    if real_image_code is None:
        # 表示验证码已过期
        return jsonify(errno=RET.NODATA, errmsg=u"图片验证码失效")

    # 删除图片验证码，防止用户用同一个验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写值对比
    if real_image_code.lower() != image_code.lower():
        # 数据不想等
        return jsonify(errno=RET.DATAERR, errmsg=u"图片验证码错误")

    # 判断60s内是否有过发送短信的操作
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg=u"请求频繁，请60秒后再尝试！")

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 说明手机号已存在
            return jsonify(errno=RET.DATAEXIST, errmsg=u"手机号已存在")

    # 如果手机号不存在，生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存手机验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存短信发送记录
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u"保存短信验证码失败")

    # 发送短信
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=u"第三方库调用异常")

    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg=u"发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg=u"发送失败")














