# coding:utf-8
import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "adsgayh164"

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@192.168.80.133:3306/ihome_flask"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行加密处理
    PERMANENT_SESSION_LIFETIME = 3600*24  # session数据的有效期


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}