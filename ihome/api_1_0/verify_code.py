# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET


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
def get_sms_code(moblie):
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

    # 与用户填写值对比
    if real_image_code.lower() != image_code.lower():
        # 数据不想等
        return jsonify(errno=RET.DATAERR, errmsg=u"数据错误")