#-*-coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
import logging
log = logging.getLogger('siyu.debug')

# Create your views here.

def CreateWeixinPayUrl(serial_id,totalpay,property,code,openid,order_ip):
    '''
    '''
    from wzhifuSDK import *

    corpid = u'wx566be73406574c97'
    mch_id = u'1491310452'
    nonce_str = Common_util_pub().createNoncestr()
    trade_type = u'JSAPI'

    notify_url = u'http://xydapi.tederen.com/common/wxpay/notify_url/'#%s/' % out_trade_no
    #预下单获取prepay_id
    order_obj = UnifiedOrder_pub()
    order_obj.setParameter('appid',corpid)
    import random
    tmp = random.randint(10,99)
    nonce_str = "gfdsahjklm"
    order_obj.setParameter('out_trade_no',str(serial_id)+str(tmp))
    order_obj.setParameter('body','iphone20')
    order_obj.setParameter('total_fee',str(int(float(totalpay)*100)))
    order_obj.setParameter('notify_url',notify_url)
    order_obj.setParameter('trade_type','JSAPI')
    order_obj.setParameter('openid',openid)
    order_obj.setParameter('mch_id', mch_id)
    order_obj.setParameter('spbill_create_ip',order_ip)
    order_obj.setParameter('nonce_str',nonce_str)

    sign = Common_util_pub().getSign(order_obj.parameters)
    print('>>>>>>>>>>>>>>>>>>>>>')
    order_obj.setParameter('sign',sign)
    log.debug(4444444444444444444)
    prepay_id = order_obj.getPrepayId()
    log.debug(prepay_id)
    log.debug(555555555555)
    return prepay_id,nonce_str,str(int(time.time()))

def ForWxJsPay(request,order_number,totalpay,order_ip):
    #wx_get_code_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx361d2a34d062cafc&redirect_uri=http://devwap.lanrenzhoumo.com/order/order/forwxpay&pay_method=4&serial_id=001000160528000&order_ip=175.152.119.246&response_type=code&scope=snsapi_base&state=123#wechat_redirect'
    #totalpay = 0.1
    totalpay = totalpay
    #serial_id = '1232131231'
    serial_id = order_number 
    order_ip = '193.167.1.99'
    wx_get_code_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxbfa35fe939643016&redirect_uri=http://baoming.siyusai.com/wxjspay/?tot_ser_cip=%s_%s_%s&response_type=code&scope=snsapi_base&state=123#wechat_redirect'%(totalpay,serial_id,order_ip)
    log.debug(wx_get_code_url)
    return HttpResponseRedirect(wx_get_code_url)  

def WxJsPay(request):
    '''
    '''
    import requests
    import time
    log.debug(1111111111111111111111111)

    code = request.GET.get('code')
    tot_ser_cip = request.GET.get('tot_ser_cip')
    log.debug(code)
    code = code                                                                
    totalpay = tot_ser_cip.split('_')[0] 
    serial_id = tot_ser_cip.split('_')[1] 
    order_ip = tot_ser_cip.split('_')[2]
    #get access_token                                                       
    APPID = 'wxbfa35fe939643016'                                               
    SECRET='b02b78cf2ef7292e024a4fabec993c16'                                  
    get_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' %(APPID,SECRET,code)
    res = requests.get(get_token_url).json()                                   
    print 7777777777777777
    log.debug(res,222222222222222)
    print res
 								       
    if res.has_key('openid'):                                                 
        open_id = res['openid']                                               
    else:                                                                      
 	    open_id = ''                                                           
 								       
    prepay_id = CreateWeixinPayUrl(serial_id,totalpay,property,code,open_id,order_ip)
    return render_to_response('wapWeixinJsPay.html',{'prepay_id':prepay_id,'nonce_str':'gfdsahjklm','price_property': "prop",'timestamp':str(int(time.time()))})


if __name__ == "__main__":
    serial_id = "123456"
    totalpay = 0.01
    property = u"测试"
    order_ip = "127.0.0.1"
    open_id = "oZdoUwnlx6yaCKaS8u15Co2YoZT8"
    prepay_id = CreateWeixinPayUrl(serial_id,totalpay,property,None,open_id,order_ip)
    print prepay_id
