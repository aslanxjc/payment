#-*- coding:utf-8 -*-
rootUrl = 'http://xydapi.tederen.com/'
class settings:
  # 安全检验码，以数字和字母组成的32位字符
  #ALIPAY_KEY = 'c9yi617kzso8gg4wwfuxi7kofb9ppgdd'
  ALIPAY_KEY = 'yhfme9yh6w9mmoxvcpmo53f1xx49pxi0'

  ALIPAY_INPUT_CHARSET = 'utf-8'

  # 合作身份者ID，以2088开头的16位纯数字
  #ALIPAY_PARTNER = '2088221719272320'
  ALIPAY_PARTNER = '2088321018260401'

  # 签约支付宝账号或卖家支付宝帐户
  #ALIPAY_SELLER_EMAIL = 'saishi@siyusai.com'
  ALIPAY_SELLER_EMAIL = 'donlee213@outlook.com'

  ALIPAY_SIGN_TYPE = 'MD5'

  # 付完款后跳转的页面（同步通知） 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
  ALIPAY_RETURN_URL=rootUrl+'alipay/return_url/'
  ALIPAY_RETURN_URL='http://xydapi.tederen.com/#/mall/success'

  # 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
  ALIPAY_NOTIFY_URL=rootUrl+'alipay/notify_url/'
  #ALIPAY_NOTIFY_URL='http://115.28.186.27:12005/common/alipay/notify_url/'
  ALIPAY_NOTIFY_URL='http://xydapi.tederen.com/common/alipay/notify_url/'

  ALIPAY_SHOW_URL='test.tederen.com'

  # 访问模式,根据自己的服务器是否支持ssl访问，若支持请选择https；若不支持请选择http
  ALIPAY_TRANSPORT='http'
  
