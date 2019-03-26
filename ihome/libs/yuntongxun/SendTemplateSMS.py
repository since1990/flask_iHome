# coding=utf-8


from CCPRestSDK import REST

#主帐号
accountSid= '8aaf0708697b6beb0169b27a97121fc2'

#主帐号Token
accountToken= 'fa03e2adb9ce49b4a420d474b0052c5d'

#应用Id
appId='8aaf0708697b6beb0169b27a97701fc9'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id


class CCP(object):
    """自己封装的发送短信的辅助类"""
    instance = None

    def __new__(cls, *args, **kwargs):
        # 单例模式
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj
        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        # for k, v in result.iteritems():
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送成功
            return 0
        else:
            return -1


if __name__ == '__main__':
    ccp = CCP()
    ccp.send_template_sms("13601968924", ["1234", "3"], 1)
