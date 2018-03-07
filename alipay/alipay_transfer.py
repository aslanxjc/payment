#-*- coding: utf-8 -*-
'''
Created on 2018-01-04
支付宝转账接口
@author: aslanxjc
'''
import json
import time,datetime
#from urllib import urlencode, urlopen
#import urllib2
import requests
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.Hash import SHA256
from config import settings
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode
try:
    import urllib2
except:
    from urllib import request as urllib2


class AlipayTransfer:
    def __init__(self):
        """支付宝转账相关
        """
        self.root_url = "https://openapi.alipay.com/gateway.do"
        #self.app_id = "2088321018260401"
        self.app_id = "2016062501553721"
        self.version = "1.0"
        self.charset = "utf-8"
        self.sign_type = "RSA2"
        #self.sign_type = "RSA"
        self.payee_type = "ALIPAY_LOGONID"
        self.pubkey = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvg8jH/4mSPK3rxv8h7M4
BWVE2Jh0dTHzcT3yT1O4q/rbDT0pIX3NcIsBWN8cBxAVvvezvlC7F+LY6utiuPeZ
y6C921TULDBtG9vyPmuirFnkLkv6mCsurf2itVOsfK6tb/fvrrgtxeiGu4YxeOmQ
Qaqu6JVJfebCp1nQef+2X+sPTTObd1+Ob37IGhI80tWiyj1TQ4TscYQpwOQCPVBE
UEsrEkL46pq2Bi7X7xEIoLoUF75tYB+pSns7EVyshmydLBdCppyUcZ6uzk0SBxUt
Y78KvDfzclHBArBQaJwr2GIZywDPdYnfXNA75tMd1OgQGcvRGcMwYZE0mIk2ouXJ
qQIDAQAB
-----END PUBLIC KEY-----'''
        self.privkey = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAvg8jH/4mSPK3rxv8h7M4BWVE2Jh0dTHzcT3yT1O4q/rbDT0p
IX3NcIsBWN8cBxAVvvezvlC7F+LY6utiuPeZy6C921TULDBtG9vyPmuirFnkLkv6
mCsurf2itVOsfK6tb/fvrrgtxeiGu4YxeOmQQaqu6JVJfebCp1nQef+2X+sPTTOb
d1+Ob37IGhI80tWiyj1TQ4TscYQpwOQCPVBEUEsrEkL46pq2Bi7X7xEIoLoUF75t
YB+pSns7EVyshmydLBdCppyUcZ6uzk0SBxUtY78KvDfzclHBArBQaJwr2GIZywDP
dYnfXNA75tMd1OgQGcvRGcMwYZE0mIk2ouXJqQIDAQABAoIBAGHpJm063rpB4ALj
5gp6d2fALeFvWL9vRjyWbxgSx1ZB20tMsL3CM23BDqab+bJhxPImZYCr0laR1LHh
JXCojaBrZKNzZgKFyA/MFVW22Yz0miqHlceCp3+W5JWJT5jD3DGMhvt5gossKQy+
KwphOKG7rnO/RKcJlEnmaRIQfAGZEVwBnzYeLCl14sMUG8S14K/o/0lMBzPHSKAS
lOY6f8nzEzfozYvm/7xVXutNteVJ4FjbIVYtVRyWg/qMjvR/NY4dK+1uSkFD8zTJ
kMUeLqAeIit9xQXSwBhfLoFp+AFc5FKXtk6TnlH9zYX77GbiguEaT4Skf9l2piLc
Qb+Ln4kCgYEA479gdJLugofcFPb9I9eJK5/0VA7y3IVaFcb369R8jTyVRVIWxj/d
LhGXUqrLQAzscHjOW9q1/HMTdbYPka/hCcrkxrQP8H8Ae0l5j8czfUzEenMH/n6y
U4ncf0ndyOOGIB6BuMJHWvbvohWcsTxLwE7WuGl1gydMvXFQZou+i4sCgYEA1aLh
q7WOX5pmYw8DNi7kg54C8NeGAJO38X74eE71ymySHUri9IfbVT+yFIKM5e3erBPN
lPIzhsNE4x4PmXUnjA9kTQHdRmX59gENRooyq7hQLtLLeESuaUcnBTzT0a5ZucXC
0uU6n+UgMPfbbnCsnacZLzOSQ551a8h/nQ/RdhsCgYEA1Je4ehkN+1rG3esQsXxo
1wghErZBjggM53crxkA7Y7vBu0u9ZqIG3RIep1Q3Fjr6GqMqPiQS7OyepaqlLeF3
t6RlmfZLSrvCv1L+3m+caMJYRdVLCQ1LeR+fbFKPbQ62DRVtEgKIiSko16xE8EzQ
iVsOpGYNA7iTseMsogygebECgYBiijfXcO4T0O8LIACWPHjw8LBgkLjhiUFeJffL
3nfm/79BvaoDqqqTnsawSSteXyLHcnbwDeuQbH9Y1yPQ38X3B553GrYK47yxKPkL
oXEP3fs2LcrmVZ+xNb2c39rAK9B9LOfZSRyKZjA8Bgdz4IruSQYHzJzZjbyRk7Cx
LHusIwKBgQDX0jxe1g/5VDwLRPCegT0Nx+LDmrX7QZdUOxhVvXASrRkBydpGL7TL
YjAVIyChx4R7KpJ1GHF2q7+wZFEHua3aZRxvI381s2MBhO6mYuvaPE+mLYOlkbNr
NlH5a/ZBljAiLFUaVt+s/kCJCYESw5eE8lzVCcEPxdL2+5uBexqzJA==
-----END RSA PRIVATE KEY-----'''

    def gen_timestamp(self):
        """
        """
        now = datetime.datetime.now()
        timestamp = datetime.datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
        return timestamp

    def test_sign(self):
        """测试用私钥签名
        """
        msg = "123456"
        key = RSA.importKey(self.privkey)
        h = SHA.new(msg)
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(h)
        signature = base64.b64encode(signature)
        return signature

    def test_verify(self):
        """测试用公钥验签
        """
        msg = "1234567"
        key = RSA.importKey(self.pubkey)
        h = SHA.new(msg)
        verifier = PKCS1_v1_5.new(key)
        ######
        signature = self.test_sign()
        flag = verifier.verify(h, base64.b64decode(signature))
        print flag

    def _signature(self,data):
        """签名
        """
        key = RSA.importKey(self.privkey)
        #h = SHA.new(data.encode("utf-8"))
        h = SHA256.new(data.encode("utf-8"))
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(h)
        #return signature
        signature = base64.b64encode(signature).decode("utf-8")
        return signature

    def _verify(self,data="123456"):
        """验签
        """
        key = RSA.importKey(self.pubkey)
        h = SHA.new(data)
        verifier = PKCS1_v1_5.new(key)
        ######
        signature = self.test_sign()
        flag = verifier.verify(h, base64.b64decode(signature))
        return flag


    def gen_sign(self,params={}):
        """生成签名
        """
        #排序组装
        ks = params.keys()
        ks.sort()
        print ks,2222222222222222
        #sortparams = {}
        prestr = ''
        for k in ks:
            v = params[k]
            #k = smart_str(k, settings.ALIPAY_INPUT_CHARSET)
            if k not in ('sign',) and v != '':
                prestr += '%s=%s&' % (k, params[k])
                #prestr += '%s=%s&amp;' % (k, params[k])
        prestr = prestr[:-1]
        print "prestr:"
        print prestr
        #用商户私钥进行RSA2签名并进行BASE64编码
        sign = self._signature(prestr)
        return sign
        return sortparams,prestr


    def transfer_to_account(self,out_biz_no,payee_account,amount):
        """转账到单个支付宝账号接口
        """
        method = "alipay.fund.trans.toaccount.transfer"
        sys_params = {
                "app_id":self.app_id, 
                "method":method, 
                "charset":self.charset, 
                "sign_type":self.sign_type, 
                "timestamp":self.gen_timestamp(), 
                "version":self.version, 
                #"biz_content":"test", 
            }
        req_params = {
                "out_biz_no":out_biz_no, 
                "payee_type":self.payee_type, 
                "payee_account":payee_account, 
                "amount":amount, 
            }
        sys_params.update({"biz_content":json.dumps(req_params)})

        params = sys_params.copy()
        params.update(req_params)

        sign = self.gen_sign(params)
        print "sign:"
        print sign
        sys_params.update({"sign":sign})
        print sys_params,1111111111111111
        querys = urlencode(sys_params)
        print req_params,22222222222222222
        post_data = urlencode(req_params)
        url = "{0}?{1}".format(self.root_url, querys)
        #response = urllib2.urlopen(url, post_data).read().decode("utf-8")
        #response = urllib2.urlopen(url, post_data)
        try:
            response = requests.post(url,data=req_params)
            rsp = response.json().get("alipay_fund_trans_toaccount_transfer_response")
            print rsp,11111111111111111111111111
            code = rsp.get("code")
            if code == "10000":
                order_id = rsp.get("order_id")
                out_biz_no = rsp.get("out_biz_no")
                return (order_id,out_biz_no)
            else:
                return False
        except:
            return False



if __name__ == "__main__":
    alipay_transfer = AlipayTransfer()
    #alipay_transfer.test_encrypt_decrypt()
    #alipay_transfer.test_verify()

    ###################
    out_biz_no = str(int(time.time()))
    payee_account = "15982456282"
    amount = 0.1 
    alipay_transfer.transfer_to_account(out_biz_no,payee_account,amount)
        
