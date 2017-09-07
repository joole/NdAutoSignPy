#!/usr/bin/python
# -*- coding: UTF-8 -*-
#coding=utf-8 

import NdHttpClient
import NdCalculateUtil
import json
import re
import time
import random
import sys

HOST = "sign-daily-completion.sdp.101.com"
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0"
URL = "https://aqapi.101.com/v0.93/tokens"
UC_SERVER = "aqapi.101.com"

class NdUser():
    def __init__(self, username, pwd, org):
        self.__username      = username 
        self.__password      = pwd
        self.__orgid         = org
        self.__tokeninfo     = ""
        self.__blesslist     = []
        self.__flowerlist    = {}

    def getJsonValue(self, jsonValue, key):
        json_to_python = json.loads(jsonValue)
        return json_to_python[key]

    def LoginToUCenter(self):
        httpclient  = NdHttpClient.NdHttpClient()
        url         = "https://"+ UC_SERVER + "/v0.93/tokens"
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kPost)    
        httpclient.AddRequestHeader("Content-type", "application/json");
        httpclient.AddRequestHeader("Connection", "keep-alive");
        httpclient.AddRequestHeader("Host", UC_SERVER);
        httpclient.AddRequestHeader("Referer", url);  #"https://aqapi.101.com/v0.93/tokens"
        httpclient.AddRequestHeader("Accept", "application/json");
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        util        = NdCalculateUtil.NdCalculateUtil()
        md5_pwd     = util.md5Encrypt(self.__password)
        posFields   = "{\"login_name\":\"" + str(self.__username) + "@" + self.__orgid + "\", \"password\":\"" + md5_pwd + "\"}"  
        httpclient.SetPostFields(posFields)
        code        = httpclient.ExecRequest()
        if code <= 0:
            return False
        token_info  = httpclient.GetResponseContent()
        #json_to_python = json.loads(token_info)
        self.__tokeninfo = token_info
        return True

    def CalcAuthorithem(self, token_info, http_method, host, path):
        mic = random.randint(0, 1000)
        util = NdCalculateUtil.NdCalculateUtil()
        nonce  = str(int(time.time() *1000) + int(mic)) +":" + str(util.generateMixRandomCode(8))
        rawMac = nonce + "\n" + http_method + "\n" + path + "\n" + host + "\n"
        
        mac_key = self.getJsonValue(self.__tokeninfo, "mac_key")
        mac = util.encryptHMac256(rawMac, mac_key)
        access_token = self.getJsonValue(self.__tokeninfo, "access_token")
        authorization = "MAC id=\"" + access_token + "\",nonce=\"" + nonce + "\",mac=\"" + mac + "\""
        return authorization

    def AutoSign(self):
        host = "im-sign.sdp.101.com"
        path = "/v2/api/signs"
        url = "https://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "GET", "im-sign.sdp.101.com", path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kGet)    
        httpclient.AddRequestHeader("Host", "im-sign.sdp.101.com")
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-type", "application/json")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        code = httpclient.ExecRequest()
        if code <= 0 :
            return False
        print httpclient.GetResponseContent()
        return True

    def GetBlessList(self):
        host = "im-birthday.social.web.sdp.101.com"
        path = "/v0.1/birthday_users"
        url = "http://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "GET", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kGet)    
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        code = httpclient.ExecRequest()
        if code <= 0:
            return []
        else:
            birth_user = []
            user_info = self.getJsonValue(httpclient.GetResponseContent(), "items")
            for item in user_info:
                birth_user.append(item["user_id"])
            print httpclient.GetResponseContent()
            return birth_user


    def BlessBirthday(self, f_user_id):
        host = "im-birthday.social.web.sdp.101.com"
        path = "/v0.1/birthday_users/" + f_user_id + "/actions/bless"
        url = "http://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "POST", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kPost)    
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-type", "application/json")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        httpclient.SetPostFields("")
        code = httpclient.ExecRequest()
        if code <= 0:
            return False
        elif code == 400:
            print("already blessed")
        else:
            print("response code : %d \n content = %s" % (code,httpclient.GetResponseContent()))
            return True
    
    def GetFlowerList(self):
        return ["768696", "443519", "624130"]

    def SendFlower(self, count, recvid):
        host = "pack.web.sdp.101.com"
        path = "/c/flower/send"
        url  = "http://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "POST", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kPost)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-type", "application/json")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        post_field = "{\"amount\":" + str(count) + ",\"dest_uid\":" + str(recvid) + ", \"item_type_id\":20000}"
        httpclient.SetPostFields(post_field)
        code = httpclient.ExecRequest()
        if code <= 0:
            return False
        else:
            print("response code : %d \n content = %s" % (code,httpclient.GetResponseContent()))
            return True

    def AutoDayClear(self):
        url = "https://sign-daily-completion.sdp.101.com/#/daily?auth=#auth#"
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kGet)    
        httpclient.AddRequestHeader("Host", "sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "*/*")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-type", "application/json")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        code = httpclient.ExecRequest()
        if code <= 0:
            return False
        else:
            return True
            

if __name__ == '__main__':
    config = None
    with open("/media/joole/LinuxDepot/Projects/LuaProjects/guard-card-server/cluster-ready/client/python_client/config.json", "r") as load_f:
        config = json.load(load_f, encoding="ascii")
        print(config)
    org_id = config["org_id"].encode('utf-8')
    users = config["users"]
    for single in users:
        user = NdUser(single["user_uid"].encode('utf-8'), single["user_pwd"].encode('utf-8'), org_id)
        user.LoginToUCenter()
        user.AutoSign()
        blessList = user.GetBlessList()
        for item in blessList:
            user.BlessBirthday(item) 
        flowList = single["send_flower_list"]
        for item in flowList:
            user.SendFlower(item["count"], item["recv_uid"].encode("utf-8"))
        user.AutoDayClear()

