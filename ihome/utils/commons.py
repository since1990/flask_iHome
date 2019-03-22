# coding:utf-8

from werkzeug.routing import BaseConverter


class ReConverter(BaseConverter):
    """自定义转换器"""
    def __init__(self, url_map, regex):
        # 调用父类初始化方法
        super(ReConverter, self).__init__(url_map)
        self.regex = regex
