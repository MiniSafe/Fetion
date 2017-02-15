# coding:utf-8
import json
import urllib
import threading
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import re
import urllib
import urllib2
import cookielib
class CookieBrowser(object):
    # 构造方法，用来传递初值
    def __init__(self):
        self.cookie=cookielib.MozillaCookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
    def getCookies(self):
        return self.cookie
    def open(self,addr,param):
        return self.opener.open(addr,param)
    def read(self,addr):
        return self.opener.open(addr).read()
    def post(self,url,**param):
        postdata=urllib.urlencode(param)
        return self.opener.open(url,postdata)
    def rawpost(self,url,param):
        return self.opener.open(url,param)

def getT():
    times=str(time.time()).replace('.','')+'0'
    return times+((13-len(times))*'0')

class Fetion:
    def __init__(self,username):
        self.brow=CookieBrowser()
        self.ssid=''
        self.phone = username
        self.info = {}
        self.loginStatus=False
        self.count=7
        self.friend=[]
    def getInfo(self):
        postdata=urllib.urlencode({
            'ssid':self.ssid
        })
        ret=json.loads(self.brow.open('http://webim.feixin.10086.cn/WebIM/GetPersonalInfo.aspx?Version=1',postdata).read())
        if ret['rc'] == 200:
            self.info=ret['rv']
            return True
        return False
    def heartbeat(self):
        while True:
            time.sleep(4)
            url='http://webim.feixin.10086.cn/WebIM/GetConnect.aspx?Version='+str(self.count)
            self.count+=1
            # print url
            data=json.loads(self.brow.post(url,reported='',ssid=self.ssid).read())
            if data['rc']==200:
                self.friend=data['rv']

    def getVerify(self):
        postdata = urllib.urlencode({
            'uname': self.phone
        })
        result=self.brow.open('http://webim.feixin.10086.cn/WebIM/GetSmsPwd.aspx',postdata).read()
    def login(self,check):
        postdata = urllib.urlencode({
            'AccountType': '1',
            'Ccp': '',
            'OnlineStatus':'400',
            'Pwd':check,
            'UserName':self.phone
        })
        result=self.brow.open('http://webim.feixin.10086.cn/WebIM/Login.aspx',postdata).read()
        if json.loads(result)['rc']==200:
            for x in self.brow.getCookies():
                x=str(x)
                if 'webim_sessionid' in x:
                    self.ssid=x.split('=')[1].split(' for ')[0]
            self.brow.read('http://webim.feixin.10086.cn/SetCounter.aspx?Version=0&coutertype=500300002,500200016,500800002&tag=default&val=1&rand=0.7514041980337672')
            self.loginStatus = self.getInfo()
            if self.loginStatus:
                self.brow.post('http://webim.feixin.10086.cn/WebIM/GetCredit.aspx?Version=2', ssid=self.ssid)
                self.brow.read('http://webim.feixin.10086.cn/WebIM/GetBackground.aspx?Version=3&uid=' + str(
                    self.info['uid']) + '&mn=' + self.phone + '&ssid=' + self.ssid + '&_=' + getT())
                self.brow.read(
                    'http://webim.feixin.10086.cn/WebIM/GetContactList.aspx?Version=4&ssid=' + self.ssid + '&_=' + getT())
                self.brow.post('http://webim.feixin.10086.cn/WebIM/GetGroupList.aspx?Version=5', ssid=self.ssid)
                self.brow.post('http://webim.feixin.10086.cn/WebIM/GetALInfo.aspx?Version=6', ssid=self.ssid)
                threading.Thread(target=self.heartbeat).start()
            return True
        return False
    def send2me(self,message):
        result=self.brow.post('http://webim.feixin.10086.cn/Views/WebIM/SendSMS.aspx?Version='+str(self.count),Msg=message,ssid=self.ssid,Receivers=str(self.info['uid']),UserName=str(self.info['uid'])).read()
        self.count+=1
        result=json.loads(result)
        if result.get('rc','') == 200:
            return True
        return False
    def sendbyPhone(self,phone,message):
        for user in self.friend:
            if user['Data'].get('mn','')==str(phone):
                result = self.brow.post('http://webim.feixin.10086.cn/WebIM/SendMsg.aspx?Version=' + str(self.count),
                                        IsSendSms=1, Msg=message, ssid=self.ssid,To=user['Data']['uid']).read()
                self.count+=1
                if json.loads(result)['rc'] == 200:
                    return True
                return False
        return False

def getTime():
    times=time.struct_time(time.localtime())
    return str(times.tm_year)+'年'+str(times.tm_mon)+'月'+str(times.tm_mday)+'日 '+str(times.tm_hour)+':'+str(times.tm_min)+':'+str(times.tm_sec)
fetion=Fetion('手机号')
fetion.getVerify()
vc=raw_input('VerifyCode:')
print fetion.login(vc)
print '获取用户信息中'
while True:
    if len(fetion.friend)>0:
        print '用户信息获取成功'
        break

print fetion.send2me(getTime()+' 短信发送平台初始化完成')

import socket
port=8081
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(('',port))
print('已初始化完成...')
while True:
    #接收一个数据
    data,addr=s.recvfrom(1024)
    print 'Received:',data
    if fetion.send2me(getTime()+'\n'+data):
        print '发送成功'
    else:
        print '发送失败'
