#coding=utf-8
#python2.7
#QianXiao
#代码只供参考学习
import requests
import json
import random
import time
import os
import sys
import traceback
import numpy as np
from collections import OrderedDict
import urllib
import xml.sax
import re

#exit()
#解决Anisi编码问题
reload(sys)
sys.setdefaultencoding('utf8')

my_headers = [
	    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
	    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
	    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
	    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
	    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
	    'Opera/9.25 (Windows NT 5.1; U; en)',
	    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
	    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
	    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'
	    ] 
myuseragent = random.choice(my_headers)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

def lzuLoginGetTAG(username,password):
  headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": myuseragent,
                "Host": "appservice.lzu.edu.cn",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
        }  
  data = {
      'username':username,
      "password":password
  }
  r = requests.post(url="https://appservice.lzu.edu.cn/api/lzu-cas/v1/tickets",headers=headers,data=urllib.urlencode(data))
  #print(r.text)
  #exit()
  if is_json(r.text):
    jsondata = json.loads(r.text)
    action = jsondata['action']
    tag = re.findall('.([^/]*)$', action)[0]
    return tag
  else:
    return None

def getStByTAG(tag):
  headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": myuseragent,
                "Host": "appservice.lzu.edu.cn",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
        }  
  r = requests.post(url="https://appservice.lzu.edu.cn/api/lzu-cas/v1/tickets/{}".format(tag),headers=headers,data="service=http://127.0.0.1")
  st = r.text
  return st

def getUserInfoBySt(st):
  headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": myuseragent,
                "Host": "appservice.lzu.edu.cn",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
        }  
  data="ticket="+st+"&service=http://127.0.0.1"
  r = requests.post(url="https://appservice.lzu.edu.cn/api/lzu-cas/serviceValidate",headers=headers,data=data)
  data = dict()
  data['cardid'] = re.findall(".*<cas:uid>(.*)</cas:uid>.*",r.text)[0]
  data['name'] = re.findall(".*<cas:cn>(.*)</cas:cn>.*",r.text)[0]
  return data

def getAccessToken(st,personid):
  headers = {
                "Host": "appservice.lzu.edu.cn",
                "Connection": "Keep-Alive",
                "User-Agent": myuseragent+' lzdx_ua JHZF_LZDXAPP',
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "com.hzsun.smartandroid",
                "Referer": "http://appservice.lzu.edu.cn/dailyReportAll/",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }  
  url = "http://appservice.lzu.edu.cn/dailyReportAll/api/auth/login?st={0}&PersonID={1}".format(st,personid)
  r = requests.get(url=url,headers=headers)
  jsondata = json.loads(r.text)
  assesstoken = None
  if jsondata['code']==1:
    assesstoken = jsondata['data']['accessToken']
  return assesstoken

def getMd5(cardid,token):
  headers = {
                "Host": "appservice.lzu.edu.cn",
                "Connection": "Keep-Alive",
                "Authorization": token,
                "Origin": "http://appservice.lzu.edu.cn",
                "User-Agent": myuseragent+' lzdx_ua JHZF_LZDXAPP',
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "X-Requested-With": "com.hzsun.smartandroid",
                "Referer": "http://appservice.lzu.edu.cn/dailyReportAll/",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
  url = "http://appservice.lzu.edu.cn/dailyReportAll/api/encryption/getMD5"
  data = "cardId={}".format(cardid)
  r = requests.post(url=url,headers=headers,data=data)
  jsondata = json.loads(r.text)
  _md5 = None
  if jsondata['code']==1:
    _md5 = jsondata['data']
  return _md5

def getInfo(cardid,md5,token):
  headers = {
                "Host": "appservice.lzu.edu.cn",
                "Connection": "Keep-Alive",
                "Authorization": token,
                "Origin": "http://appservice.lzu.edu.cn",
                "User-Agent": myuseragent+' lzdx_ua JHZF_LZDXAPP',
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "com.hzsun.smartandroid",
                "Referer": "http://appservice.lzu.edu.cn/dailyReportAll/",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
  url = "http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/getInfo"
  data = "cardId={0}&md5={1}".format(cardid,md5)
  r = requests.post(url=url,headers=headers,data=data)
  jsondata = json.loads(r.text)
  return jsondata

def submitInfo(_info, token):
    _sbinfo = OrderedDict()
    _sbinfo["bh"] = _info["bh"];#编号
    _sbinfo["xykh"] = _info["xykh"];#校园卡号
    _sbinfo["twfw"] = _info["twfw"];#0;#体温范围
    _sbinfo["jkm"] = _info["jkm"];#0;#健康码
    _sbinfo["sfzx"] = "0" if _info["sfzx"]==None else _info["sfzx"];#是否在校
    _sbinfo["sfgl"] = "0" if _info["sfgl"]==None else _info["sfgl"];#是否隔离
    _sbinfo["szsf"] = "" if _info["szsf"]==None else _info["szsf"];#现住省
    _sbinfo["szds"] = "" if _info["szds"]==None else _info["szds"];#现住市
    _sbinfo["szxq"] = "" if _info["szxq"]==None else _info["szxq"];#现住县
    _sbinfo["sfcg"] = "0" if _info["sfcg"]==None else _info["sfcg"];#是否出国
    _sbinfo["cgdd"] = "" if _info["cgdd"]==None else _info["cgdd"];#出国地点
    _sbinfo["gldd"] = "" if _info["gldd"]==None else _info["gldd"];#隔离地点
    _sbinfo["jzyy"] = "" if _info["jzyy"]==None else _info["jzyy"];#就诊医院
    _sbinfo["bllb"] = "0" if _info["bllb"]==None else _info["bllb"];#是否列入疑似/确诊病例类型
    _sbinfo["sfjctr"] = "0" if _info["sfjctr"]==None else _info["sfjctr"];#是否接触他人
    _sbinfo["jcrysm"] = "" if _info["jcrysm"]==None else _info["jcrysm"];
    _sbinfo["xgjcjlsj"] = "" if _info["xgjcjlsj"]==None else _info["xgjcjlsj"];#相关进出经历日期
    _sbinfo["xgjcjldd"] = "" if _info["xgjcjldd"]==None else _info["xgjcjldd"];#相关进出经历地点
    _sbinfo["xgjcjlsm"] = "" if _info["xgjcjlsm"]==None else _info["xgjcjlsm"];#相关进出经历说明
    _sbinfo["zcwd"] = '0.0';#早晨温度
    _sbinfo["zwwd"] = '0.0';#中午温度
    _sbinfo["wswd"] = '0.0';#晚上温度
    _sbinfo["sbr"] = _info["xm"];#上报人
    _sbinfo["sjd"] = "";#时间段
    _sbinfo["initLng"] = "";#经度
    _sbinfo["initLat"] = "";#维度
    _sbinfo["dwfs"] = "";#定位方式
    url='http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/submit'
    headers = {
              "Host": "appservice.lzu.edu.cn",
              "Connection": "Keep-Alive",
              "Authorization": token,
              "Origin": "http://appservice.lzu.edu.cn",
              "User-Agent": myuseragent+' lzdx_ua JHZF_LZDXAPP',
              "Content-Type": "application/x-www-form-urlencoded",
              "Accept": "*/*",
              "X-Requested-With": "com.hzsun.smartandroid",
              "Referer": "http://appservice.lzu.edu.cn/dailyReportAll/",
              "Accept-Encoding": "gzip, deflate",
              "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    r = requests.post(url=url,headers=headers,data=urllib.urlencode(_sbinfo))
    jsondata = json.loads(r.text)
    poststate = jsondata["code"]
    if poststate==1:
        print("上报成功")
    else:
        print("上报失败")

def punch(cardid, password):
    tag = lzuLoginGetTAG(cardid, password)
    if tag == None:
        print "用户登录失败"
        return
    print(tag)
    st = getStByTAG(tag)
    print(st)
    token = getAccessToken(st, cardid)
    if token == None:
        print "AccessToken获取失败"
        return
    _md5 = getMd5(cardid, token)
    if _md5 == None:
        print "MD5获取失败"
        return
    print(_md5)
    jsondata = getInfo(cardid, _md5, token)
    if jsondata["code"] == 0:
        print "获取用户信息失败"
        return
    
    _info = jsondata["data"]['list'][0]
    if _info['sbzt'] == "1":
        print("{}今日已上报\t上报时间：{}\n".format(_info["xm"],_info["sbsj"]))
        return
    print("正在打卡")
    submitInfo(_info, token)
    return

punch('000000000000', '******')
