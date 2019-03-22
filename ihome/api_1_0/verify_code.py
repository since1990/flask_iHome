# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from flask import current_app, jsonify, make_response
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
        return jsonify(errno=RET.DBERR, errmsg="save image code failed!")

    # 返回图片数据
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp
