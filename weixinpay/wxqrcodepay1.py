#-*-coding=utf-8 -*-
import random
import traceback
import pycurl
import StringIO
import logging
from hashcompat import md5_constructor as md5
import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
import datetime
import re
import time

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
    #sign = md5(prestr+'&key=22c0bbf67e5939b8933ca9a3ce8b3bb9').hexdigest()
    sign = md5(prestr+'&key=gfdsaHJKLMtrewqYUIOP65726NBVCXhj').hexdigest()
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
def getQrcodeUrl(order_number,good_name,totalpay):
    qrcode_url = ''
    parameters = dict()
    #商品描述
    parameters['body'] = good_name
    #商品订单号
    #订单号后随机加2位 以支持订单过期能支付和改价
    tmp = random.randint(10,99)
    parameters['out_trade_no'] = str(order_number)+str(tmp)
    #总价
    parameters['total_fee'] = str(int(totalpay*100))
    #支付回调地址
    parameters['notify_url'] = 'http://baoming.siyusai.com/weixin_qrcode_notify/'
    #交易类型 选用NATIVE
    parameters['trade_type'] = 'NATIVE'

    #parameters['appid'] = 'wx3306d928595c4c08'

    #parameters['mch_id'] = '10058963'
    parameters['appid'] = 'wxbfa35fe939643016'

    parameters['mch_id'] = '1333394901'

    parameters['nonce_str'] = random_str()

    #生成签名
    parameters['sign'] = getSign(parameters)
    #log.debug('weixn_qrcode sign:%s'%parameters['sign'])
    #print 'sign:',parameters['sign']
    #把字典转成xml
    xmlStr = array2Xml(parameters)
    #print 'pre xmlStr:',xmlStr
    #log.debug('weixn_qrcode prexmlStr:%s'%xmlStr)
    #向微信服务器验证
    veryfiXml = postXmlCurl(xmlStr,"https://api.mch.weixin.qq.com/pay/unifiedorder")
    #print 'aft xmlStr:',veryfiXml
    #log.debug('weixn_qrcode aft xmlStr:%s'%veryfiXml)
    #把xml结果转换成字典 二维码url存放在此
    qrCodeUrlResultDict = xml2Array(veryfiXml)
    
    if "FAIL" == qrCodeUrlResultDict["return_code"]:
        print 'return_mdg:',qrCodeUrlResultDict["return_msg"]
        #log.debug('weixn_qrcode return_mdg:%s'%qrCodeUrlResultDict["return_msg"])
    elif "FAIL" == qrCodeUrlResultDict["result_code"]:
        print 'err_code:',qrCodeUrlResultDict["err_code"]
        #log.debug('weixn_qrcode err_code:%s'%qrCodeUrlResultDict["err_code_des"])
    elif '' != qrCodeUrlResultDict["code_url"]:
        #log.debug('weixn_qrcode code_url:%s'%qrCodeUrlResultDict["code_url"])
        qrcode_url = qrCodeUrlResultDict["code_url"]
        #print qrCodeUrlResultDict["code_url"]
    else:
        pass
    return qrcode_url

if __name__ == "__main__":
    print getQrcodeUrl('12312312','test',0.1)



    
    
