from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^weixin_qrcode_notify/', 'weixinpay.views.weixin_qrcode_notify'),


)
