# -*- coding: utf-8 -*-
'''
支付宝手机接口
'''
import types,time,re,logging,urllib2
from urllib import urlencode, unquote,quote
from hashcompat import md5_constructor as md5
from config import settings
log = logging.getLogger('hdj.m_website')

req_id = str(int(time.time()))

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

# 网关地址
_GATEWAY = 'http://wappaygw.alipay.com/service/rest.htm'


# 对数组排序并除去数组中的空值和签名参数
# 返回数组和链接串
def params_filter(params,isSort=True):
    ks = params.keys()
    newparams = {}
    prestr = ''
    #手机支付宝异步回调 不用参数排序
    if isSort:
        ks.sort()
        for k in ks:
            v = params[k]
            k = smart_str(k, settings.ALIPAY_INPUT_CHARSET)
            if k not in ('sign','sign_type') and v != '':
                newparams[k] = smart_str(v, settings.ALIPAY_INPUT_CHARSET)
                prestr += '%s=%s&' % (k, newparams[k])
        prestr = prestr[:-1]

    else:
	    prestr = 'service='+smart_str(params['service'],settings.ALIPAY_INPUT_CHARSET)+\
			'&v='+smart_str(params['v'],settings.ALIPAY_INPUT_CHARSET)+\
			'&sec_id='+smart_str(params['sec_id'],settings.ALIPAY_INPUT_CHARSET)+\
			'&notify_data='+smart_str(params['notify_data'],settings.ALIPAY_INPUT_CHARSET)
    return newparams, prestr


# 生成签名结果
def build_mysign(prestr, key, sign_type = 'MD5'):
    if sign_type == 'MD5':
        return md5(prestr + key).hexdigest()
    return ''

#为alipay.wap.trade.create.direct组装参数
#def fill_param_for_create_directt():
#    pass

def get_request_token(res_data):
    rt = re.compile(r'<request_token>(.*?)</request_token>')
    rtList = rt.findall(res_data)
    if 0 == len(rtList):
        return (0,None)
    elif 1 == len(rtList):
        return (1,rtList[0])
    else:
        return (0,None)

#手机支付接口alipay.wap.auth.authandexecute
def request_for_auth_authandexecute(request_token):
    #为alipay.wap.auth.authandexecute组装参数
    req_data = '<auth_and_execute_req><request_token>'+request_token+'</request_token></auth_and_execute_req>';

    params = {}
    params['service'] = 'alipay.wap.auth.authAndExecute'
    params['partner'] = settings.ALIPAY_PARTNER
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET
    params['sec_id'] = 'MD5'
    params['format'] = 'xml'
    params['v'] = '2.0'
    params['req_id'] = req_id
    params['req_data'] = req_data
    params,prestr = params_filter(params)
    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    return 'http://wappaygw.alipay.com/service/rest.htm?'+urlencode(params)

#手机支付接口alipay.wap.trade.create.direct
def request_for_create_direct(tn, subject, body, total_fee):
    #为alipay.wap.trade.create.direct组装参数
    req_data = '<direct_trade_create_req><notify_url>' + settings.ALIPAY_NOTIFY_URL \
               +'</notify_url><call_back_url>' + settings.ALIPAY_RETURN_URL \
               + '</call_back_url><seller_account_name>' + settings.ALIPAY_SELLER_EMAIL \
               + '</seller_account_name><out_trade_no>' + tn \
               + '</out_trade_no><subject>' + subject \
               + '</subject><total_fee>' + total_fee \
               + '</total_fee>' + '</direct_trade_create_req>';

    params = {}
    params['service'] = 'alipay.wap.create.direct.pay.by.user'
    params['partner'] = settings.ALIPAY_PARTNER
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET
    params['notify_url'] = settings.ALIPAY_NOTIFY_URL
    params['return_url'] = settings.ALIPAY_RETURN_URL
    params['out_trade_no'] = tn
    params['subject'] = subject
    params['total_fee'] = total_fee
    params['seller_id'] = settings.ALIPAY_PARTNER
    params['payment_type'] = '1'
    params,prestr = params_filter(params)
    log.debug('res ori:%s'%prestr)
    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    params['sign_type'] = 'MD5'
    #http://wappaygw.alipay.com/service/rest.htm

    log.debug('res_data param:%s'%urlencode(params))
    return 'https://mapi.alipay.com/gateway.do?'+urlencode(params)
    #request = urllib2.Request('https://mapi.alipay.com/gateway.do',urlencode(params))
    #res_data = urllib2.urlopen(request).read()
    #res_data = unquote(res_data)
    #log.debug('res_data begin:%s'%res_data)
    #flg,request_token = get_request_token(res_data)
    
#log.debug('res_data:%s'%res_data)
    #return flg,request_token

# 手机即时到账交易接口
def m_create_direct_pay_by_user(tn, subject, body, total_fee):
    return request_for_create_direct(tn, subject, body, total_fee)
    #if 1 == flg:
    #    url = request_for_auth_authandexecute(request_token)
    #    return (1,url)
    #else:
    #    return (0,None)


# 纯担保交易接口
def create_partner_trade_by_buyer (tn, subject, body, price):
    params = {}
    # 基本参数
    params['service']       = 'create_partner_trade_by_buyer'
    params['partner']           = settings.ALIPAY_PARTNER
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET
    params['notify_url']        = settings.ALIPAY_NOTIFY_URL
    params['return_url']        = settings.ALIPAY_RETURN_URL

    # 业务参数
    params['out_trade_no']  = tn        # 请与贵网站订单系统中的唯一订单号匹配
    params['subject']       = subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    params['payment_type']  = '1'
    params['logistics_type'] = 'POST'   # 第一组物流类型
    params['logistics_fee'] = '0.00'
    params['logistics_payment'] = 'BUYER_PAY'
    params['price'] = price             # 订单总金额，显示在支付宝收银台里的“应付总额”里
    params['quantity'] = 1              # 商品的数量
    params['seller_email']      = settings.ALIPAY_SELLER_EMAIL
    params['body']          = body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
    params['show_url'] = settings.ALIPAY_SHOW_URL

    params,prestr = params_filter(params)

    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    params['sign_type'] = settings.ALIPAY_SIGN_TYPE

    return _GATEWAY + urlencode(params)

# 确认发货接口
def send_goods_confirm_by_platform (tn):
    params = {}

    # 基本参数
    params['service']       = 'send_goods_confirm_by_platform'
    params['partner']           = settings.ALIPAY_PARTNER
    params['_input_charset']    = settings.ALIPAY_INPUT_CHARSET

    # 业务参数
    params['trade_no']  = tn
    params['logistics_name'] = u'大活动网'   # 物流公司名称
    params['transport_type'] = u'POST'

    params,prestr = params_filter(params)

    params['sign'] = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    params['sign_type'] = settings.ALIPAY_SIGN_TYPE

    return _GATEWAY + urlencode(params)


def notify_verify(post):
    # 初级验证--签名
    _,prestr = params_filter(post)
    log.debug('notify return param:%s'%prestr)
    mysign = build_mysign(prestr, settings.ALIPAY_KEY, settings.ALIPAY_SIGN_TYPE)
    if mysign != post.get('sign'):
        return False
    # 二级验证--查询支付宝服务器此条信息是否有效
    params = {}
    #notifyData = post.get('notify_data').encode('utf-8')
    #notifyRe = re.compile(r'<notify_id>(.*?)</notify_id>')
    #notifyList = notifyRe.findall(notifyData)
    params['partner'] = settings.ALIPAY_PARTNER
    params['notify_id'] = post.get('notify_id')
    if settings.ALIPAY_TRANSPORT == 'https':
        params['service'] = 'notify_verify'
        gateway = 'https://mapi.alipay.com/gateway.do?service=notify_verify&'
    else:
        gateway = 'http://notify.alipay.com/trade/notify_query.do?'
    veryfy_result = urllib2.urlopen(gateway+urlencode(params)).read()
    if veryfy_result.lower().strip() == 'true':
        return True
    return False

if __name__ == '__main__':
    #order_number = str(int(time.time()))
    order_number = "123456"
    spu_name = u'测试'
    spu_des = u'测试'
    totalpay = 0.1
    print m_create_direct_pay_by_user(order_number,spu_name,spu_des,str(totalpay))
