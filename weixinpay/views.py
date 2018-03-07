#encoding=utf8
import random
import traceback
import pycurl
import StringIO
#from dahuodong.models import SysOrder
#from new_event.models import NewOrder, RefundRecord
import logging
from hashcompat import md5_constructor as md5
import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
from utils.utils import SendOrderMsg, sendMail
from order.models import NewOrder, RefundRecord,SysOrder
from django.views.decorators.csrf import csrf_exempt
from payment.views import upgrade_order
import datetime
import re
import time
from usercenter.views import order_add_credit
from seo.utils import index_seo
from utils.sendcloud import send_email_by_sendcloud

log = logging.getLogger('website.debug')
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

def getSign(params):
    ks = params.keys()
    newparams = {}
    prestr = ''
    #字典序升序排列
    ks.sort()
    for k in ks:
        v = params[k]
        k = smart_str(k, 'utf-8')
        if k not in ('sign','sign_type') and v != '':
            newparams[k] = smart_str(v, 'utf-8')
            prestr += '%s=%s&' % (k, newparams[k])
    prestr = prestr[:-1]
    sign = md5(prestr+'&key=22c0bbf67e5939b8933ca9a3ce8b3bb9').hexdigest()
    return sign.upper()


def random_str():
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    rand = random.Random()
    for i in range(32):
        str+=chars[rand.randint(0, length)]
    return str

def array2Xml(parameters):
    xml = "<xml>"
    for k,v in parameters.items():
        if 'total_fee' in k or\
           'nonce_str' in k or\
           'mch_id' in k or\
           'appid' in k or\
           'transaction_id' in k or\
           'out_trade_no' in k or\
           'return_code' in k or\
           'return_msg' in k:
            xml = xml + "<"+k+">"+v+"</"+k+">"
        else:
            xml = xml + "<"+k+"><![CDATA["+v+"]]></"+k+'>'
    xml = xml+"</xml>"
    return xml

def xml2Array(xmlStr):
    array_data = {}
    root = ET.fromstring(xmlStr)
    for child in root:
        value = child.text
        array_data[child.tag] = value
    return array_data
    
    
def postXmlCurl(xmlStr,url):
    c = pycurl.Curl()
    c.setopt(pycurl.TIMEOUT, 30)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.HEADER, 0)
    #c.setopt(pycurl.RETURNTRANSFER, 0)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, xmlStr)

    f = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, f.write)
    c.perform()
    data = ''
    if c.getinfo(c.RESPONSE_CODE) == 200:
        data = f.getvalue()
    else:
        pass
    c.close()
    return data


#获取商品的微信支付二维码URL
def getQrcodeUrl(tn):
    qrcode_url = ''
    try:
        order = NewOrder.objects.get(order_number=tn)
    except Exception,e:
        return ''
        log.debug(e)
    good_name = order.event_name.encode('utf8')
    #微信支付单位是分 要乘100 另提交微信金额不能有小数点
    totalpay = str(int(order.order_totalpay*100))
    parameters = dict()
    #商品描述
    parameters['body'] = good_name
    #商品订单号
    #订单号后随机加2位 以支持订单过期能支付和改价
    tmp = random.randint(10,99)
    parameters['out_trade_no'] = str(tn)+str(tmp)
    #总价
    parameters['total_fee'] = totalpay
    #支付回调地址
    parameters['notify_url'] = 'http://www.siyusai.com/weixin_qrcode_notify/'
    #交易类型 选用NATIVE
    parameters['trade_type'] = 'NATIVE'

    parameters['appid'] = 'wx3306d928595c4c08'

    parameters['mch_id'] = '10058963'

    parameters['nonce_str'] = random_str()

    #生成签名
    parameters['sign'] = getSign(parameters)
    log.debug('weixn_qrcode sign:%s'%parameters['sign'])
    #print 'sign:',parameters['sign']
    #把字典转成xml
    xmlStr = array2Xml(parameters)
    #print 'pre xmlStr:',xmlStr
    log.debug('weixn_qrcode prexmlStr:%s'%xmlStr)
    #向微信服务器验证
    veryfiXml = postXmlCurl(xmlStr,"https://api.mch.weixin.qq.com/pay/unifiedorder")
    #print 'aft xmlStr:',veryfiXml
    log.debug('weixn_qrcode aft xmlStr:%s'%veryfiXml)
    #把xml结果转换成字典 二维码url存放在此
    qrCodeUrlResultDict = xml2Array(veryfiXml)
    
    if "FAIL" == qrCodeUrlResultDict["return_code"]:
        #print 'return_mdg:',qrCodeUrlResultDict["return_msg"]
        log.debug('weixn_qrcode return_mdg:%s'%qrCodeUrlResultDict["return_msg"])
    elif "FAIL" == qrCodeUrlResultDict["result_code"]:
        #print 'err_code:',qrCodeUrlResultDict["err_code"]
        log.debug('weixn_qrcode err_code:%s'%qrCodeUrlResultDict["err_code_des"])
    elif '' != qrCodeUrlResultDict["code_url"]:
        log.debug('weixn_qrcode code_url:%s'%qrCodeUrlResultDict["code_url"])
        qrcode_url = qrCodeUrlResultDict["code_url"]
        #print qrCodeUrlResultDict["code_url"]
    else:
        pass
    return qrcode_url

def weixin_do_notify_url_handler(order_number,trade_no):
    log.debug('weixin_qrcode enter notify handler')
    order = SysOrder.objects.get(order_number=order_number)
    log.debug('weixin_qrcode enter notify handler get order done')
    if upgrade_order(order,trade_no):
        log.debug('weixin_qrcode enter upgrade order')
        subject = u'PC站用户付款提醒(微信支付)'
        log.debug('weixin_qrcode enter upgrade order subject')
        #content = '''用户 【%s】已经付款%s元,以下是付款详情\n订单号:%s\n电话:%s\n活动名:%s\n活动id:%s\n活动链接:%s\n单价:%s\n数量:%s\n%s\n地址:%s\n付款时间:%s\n付款方式:微信扫码支付
        content = '''用户 【%s】已经付款%s元,以下是付款详情</br>订单号:%s</br>电话:%s</br>活动名:%s</br>活动id:%s</br>活动链接:%s</br>单价:%s</br>数量:%s</br>%s</br>地址:%s</br>付款时间:%s</br>付款方式:微信支付
        '''       %(  order.order_user_name.encode('utf-8'),
                               order.order_totalpay,
                               order.order_number.encode('utf-8'),
                               order.order_tel.encode('utf-8'),
                               order.event_name.encode('utf-8'),
                               order.event_id,
                               'http://www.huodongjia.com/event-%s.html'%order.event_id,
                               order.order_price,
                               order.order_amount,
                               order.order_pay_info.encode('utf-8'),
                               order.order_address.encode('utf-8'),
                               str(datetime.datetime.today()),
                               )
        log.debug('weixin_qrcode enter upgrade order content')
        #sendMail(subject,content)
        send_email_by_sendcloud(subject,content)
        log.debug('weixin_qrcode enter upgrade order sendmail')
        msgs= u'您已成功付款%s活动，预计3-24小时内为您出票。访问www.huodongjia.com查询订单号%s【活动家】'\
         % (re.sub(ur"[^\u4e00-\u9fa5\w]", "", order.event_name),order.order_number)
        log.debug('weixin_qrcode enter upgrade order ready msgs')
        SendOrderMsg(order.order_tel,msgs)
        log.debug('weixin_qrcode enter upgrade order ready send msg tel done')

#用户在微信支付后  微信回调我们 进行验证
@csrf_exempt
def weixin_qrcode_notify(request):
    if request.method == 'POST':
        log.debug('weixin_qrcode enter callback') 
        notifyData = smart_str(request.body)
        #return HttpResponse('ehello')
        log.debug('weixin_qrcode enter callback notify data:%s'%notifyData)
        notifyDict = xml2Array(notifyData)
        returnParameter = dict()
        mySign = getSign(notifyDict)
        #签名验证成功
        if mySign == notifyDict['sign']:
            returnParameter['return_code'] = 'SUCCESS'
            log.debug('weixin_qrcode enter callback sign is success:%s'%notifyDict['out_trade_no'])
        else:
            returnParameter['return_code'] = 'FAIL'
            returnParameter['return_msg'] = '签名失败'
            log.debug('weixin_qrcode enter callback sign is fail:%s'%notifyDict['out_trade_no'])
        myXml = array2Xml(returnParameter)
        HttpResponse(myXml)
        try:
            from utils.rabbitmqsender import pub_send
            pub_send('logs',notifyDict['out_trade_no'])

            #支付成功修改订单状态
            if mySign == notifyDict['sign']:
                log.debug('weixin_qrcode start modify order status')
                #微信返回的订单号后2位要去掉
                #weixin_do_notify_url_handler(notifyDict['out_trade_no'][:-2])
                log.debug(notifyDict['transaction_id'])
                weixin_do_notify_url_handler(notifyDict['out_trade_no'][:-2],notifyDict['transaction_id'])

                order = NewOrder.objects.get(order_number=notifyDict['out_trade_no'][:-2])
                
                
                try:
                    cre_val = order_add_credit(request, order.order_totalpay, notifyDict['out_trade_no'][:-2], order.order_tel)
                except Exception, e:
                    log.debug(e)
                    cre_val = 0
                data = {
                    'order_num': notifyDict['out_trade_no'][:-2],
                    'price': order.order_totalpay,
                    'cre_val': cre_val,
                    'seo': index_seo(),
                    'event_id': order.event_id,
                }
                log.debug(11111111111111111111111111)
                return render(request, 'paySuccess.html', data)
        #excp
        except:
            log.debug(traceback.format_exc())
    else:
        log.debug('weixin_qrcode enter callback is get method')
        return HttpResponse('hi get')
#getQrcodeUrl()


    
    
