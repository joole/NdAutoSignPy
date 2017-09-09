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
import logging

HOST = "sign-daily-completion.sdp.101.com"
USER_AGENT = "99U_Task_Terminator"
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
        logging.debug("LoginToUCCenter")
        httpclient  = NdHttpClient.NdHttpClient()
        url         = "https://"+ UC_SERVER + "/v0.93/tokens"
        logging.debug("LoginToUCCenter url = {}".format(url))
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
            logging.critical("can't connect to server")
            return False
        elif code >= 400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
      
            return False
        else:
            logging.debug("server response error : {}".format(httpclient.GetResponseContent()))
            token_info  = httpclient.GetResponseContent()
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
        authorization = self.CalcAuthorithem(self.__tokeninfo, "POST", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kPost)  
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN")
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Connection", "keep-alive")
        httpclient.AddRequestHeader("content-type", "application/json")
        httpclient.SetPostFields("{}")
        code = httpclient.ExecRequest()
        if code <= 0:
            logging.critical("can't connect to server")
            return False
        elif code > 400:
            logging.error("server response error : http_code = {} response= {}".format(code, httpclient.GetResponseContent()))
            return False
        elif code == 400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
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
            logging.critical("can't connect to server")
            return []
        elif code >= 400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
            return []
        else:
            birth_user = []
            user_info = self.getJsonValue(httpclient.GetResponseContent(), "items")
            for item in user_info:
                birth_user.append(item["user_id"])
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
            logging.critical("can't connect to server")
            return False
        elif code >= 400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
            return True
        else:
            return True

    def SendFlower(self, count, recvid):
        host = "pack2.sdp.101.com"
        path = "/v0.3/c/flower/send/nogami/20000/to/" + str(recvid) + "/" + str(count)
        url  = "https://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "POST", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kPost)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("Accept", "*/*")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Content-Type", "application/json")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Connection", "keep-alive")
        post_field = "{\"accept_language\":\"zh-CN\"}"
        httpclient.SetPostFields(post_field)
        code = httpclient.ExecRequest()
        if code <= 0:
            logging.critical("can't connect to server")
            return False
        elif code >= 400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
            return False
        else:
            logging.debug("p")
            return True

    def AutoDayClear(self):
        host = "sign-out.sdp.101.com"
        path = "/v2/api/signs"
        url = "https://" + host + path
        authorizatioin = self.CalcAuthorithem(self.__tokeninfo, "GET", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kGet)    
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-Type", "application/json")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        httpclient.AddRequestHeader("authorization", authorizatioin)
        code = httpclient.ExecRequest()
        if code <= 0:
            logging.critical("can't connect to server")
            return False
        elif code >=400:
            
            logging.error("service response error : {}".format(httpclient.GetResponseContent()))
            return False
        
        path = "/v2/api/signs/todo"
        url = "https://" + host + path
        authorizatioin = self.CalcAuthorithem(self.__tokeninfo, "GET", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kGet)    
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-Type", "application/json")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        httpclient.AddRequestHeader("authorization", authorizatioin)
        code = httpclient.ExecRequest()
        if code <= 0:
            logging.critical("can't connect to server")
            return False
        elif code >=400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
            return False
        else:
            return True

    def GetRewardList(self):
        host= "pbl4task.sdp.101.com"
        path = "/v0.1/userrewards"
        url = "https://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "GET", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kGet)    
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("Content-type", "application/json")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        code = httpclient.ExecRequest()
        if code <= 0:
            logging.critical("can't connect to server")
            return []
        elif code >=400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
            return []
        else:
            contents = json.loads(httpclient.GetResponseContent(), encoding="utf8")
            reward_list = []
            for reward in contents["items"]:
                if reward["reward_status"] != 1:
                    reward_list.append(reward["reward_code"].encode("utf-8"))
            return reward_list

    def GainReward(self, reward_code):
        host = "pbl4task.sdp.101.com"
        path = "/v0.1/userrewards/" + reward_code + "/actions/gain"
        url = "https://" + host + path
        authorization = self.CalcAuthorithem(self.__tokeninfo, "POST", host, path)
        httpclient = NdHttpClient.NdHttpClient()
        httpclient.SetRequestUrl(url)
        httpclient.SetRequestMethod(NdHttpClient.eRequestType.kPost)    
        httpclient.AddRequestHeader("Host", host)
        httpclient.AddRequestHeader("User-Agent", USER_AGENT)
        httpclient.AddRequestHeader("Accept", "application/json")
        httpclient.AddRequestHeader("Accept-Language", "zh-CN,zh;q=0.8")
        httpclient.AddRequestHeader("authorization", authorization)
        httpclient.AddRequestHeader("Origin", "https://sign-daily-completion.sdp.101.com")
        httpclient.AddRequestHeader("Referer", "https://sign-daily-completion.sdp.101.com/")
        httpclient.AddRequestHeader("content-Type", "application/json")
        httpclient.AddRequestHeader("Connection", "keep-alive")
        httpclient.SetPostFields("")
        code = httpclient.ExecRequest()
        if code <= 0:
            logging.critical("can't connect to server")
            return False
        elif code >= 400:
            err_code = self.getJsonValue(httpclient.GetResponseContent(), "code")
            err_msg  = self.getJsonValue(httpclient.GetResponseContent(), "message")    
            logging.error("server repsonse http_code = {} error_code = {} error_msg = {}".format(code, err_code, err_msg))
            return False
        else:
            return True


if __name__ == '__main__':
    #reload(sys)
    #sys.setdefaultencoding('utf-8')
    #logging.basicConfig(level = logging.WARNING,
    #                    format = '%s(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s:%(message)s')
 
    config = None
    with open("config.json", "r") as load_f:
        config = json.load(load_f, encoding="ascii")
    org_id  = config["org_id"].encode('utf-8')
    users   = config["users"]
    for single in users:
        user = NdUser(single["user_uid"].encode('utf-8'), single["user_pwd"].encode('utf-8'), org_id)
        if not user.LoginToUCenter() : 
            logging.error("Oops : Can't Login to UC Center, will broken to next step")
            continue
        if not user.AutoSign():
            logging.error("Oops: Can't AutoSign")
            continue
        blessList = user.GetBlessList()
        for item in blessList:
            if not user.BlessBirthday(item):
                logging.error("Oops: bless %s error, will try next one" % (item)) 
        flowList = single["send_flower_list"]
        for item in flowList:
            if not user.SendFlower(item["count"], item["recv_uid"].encode("utf-8")):
                logging.error("Oops: can't send {0} flower to {1}".format(item["count"], item["recv_uid"]))
        
        if not user.AutoDayClear():
            logging.error("Oops : can't clear day")
        
        rewardList = user.GetRewardList()
        for code in rewardList:
            user.GainReward(code)

