#!/usr/bin/python
# -*- coding: UTF-8 -*-
#coding=utf-8 

import sys
import pycurl
import time
import certifi

class Enum(set):
    def __getattr__(self, name):
      if name in self:
        return name
      raise AttributeError

eRequestType = Enum(["kHead", "kGet", "kPost"])

class NdHttpClient():
    def __init__(self):
        self.__request_url      = ''
        self.__request_headers     = []
        self.__response_headers   = {}
        self.__response_headers_str = ''
        self.__response_content   = ''
        self.__post_fields       = ''
        self.__request_mode     = eRequestType.kGet
        self.__curl_context     = pycurl.Curl()
        self.__allow_redirect     = 1
        self.__proxy_address     = ''
        self.__proxy_port       = 0
        self.__proxy_flag       = 0

    def __del__(self):
        self.__curl_context.close()

    def SetRequestUrl(self, url):
        self.__request_url  = url

    def SetRequestMethod(self, mode):
        self.__request_mode = mode

    def SetPostFields(self, postFields):
        self.__post_fields  = postFields

    def SetProxy(self, proxy_addr, proxy_port):
        self.__proxy_address  = proxy_addr
        self.__proxy_port     = proxy_port
        self.__proxy_flag     = 1

    def AddRequestHeader(self, strKey, strValue):
        self.__request_headers.append(strKey + ':' + strValue)

    def AllowRedirection(self, allow):
        self.__allow_redirect = allow

    def OnResponseHeaders(self, buf):
        tmp = buf.split(':')
        if len(tmp) < 2:
            return
        strKey   = tmp[0].lstrip()
        strKey   = strKey.rstrip()
        strValue = tmp[1].lstrip()
        strValue = strValue.rstrip()
        if tmp[0] not in self.__response_headers :
            self.__response_headers[strKey] = strValue
        else:
            tmp_content = self.__response_headers[strKey]
            tmp_content = tmp_content + ';' + strValue
            self.__response_headers[strKey] = tmp_content

        self.__response_headers_str    = self.__response_headers_str + buf

    def OnResponseContent(self, buf):
        self.__response_content  = self.__response_content + buf

    def GetResponseContent(self):
        return self.__response_content

    def GetResponseHeadersStr(self):
        return self.__response_headers_str

    def GetResponseHeaderValue(self, strKey):
        if strKey in self.__response_headers:
            return self.__response_headers[strKey]
        return ''

    def AllowAutoRedirect(self, bAllow):
        self.__allow_redirect = bAllow

    def ClearRequestResource(self):
        self.__request_url      = ''
        self.__request_headers     = []
        self.__response_headers   = {}
        self.__response_headers_str = ''
        self.__response_content   = ''
        self.__post_fields       = ''
        self.__request_mode     = eRequestType.kGet
        self.__curl_context     = pycurl.Curl()
        self.__allow_redirect     = 1
        self.__proxy_port      = 0
        self.__proxy_address    = ''
        self.__proxy_flag      = 0

    def ExecRequest(self):
        if not self.__request_url:
            return -1
        self.__curl_context.setopt(pycurl.URL, self.__request_url)
        self.__curl_context.setopt(pycurl.VERBOSE, 0)
        self.__curl_context.setopt(pycurl.HTTPHEADER, self.__request_headers)
        if self.__request_mode == eRequestType.kHead:
            self.__curl_context.setopt(pycurl.HEADERFUNCTION, self.OnResponseHeaders)
            self.__curl_context.setopt(pycurl.NOBODY, 1)
        elif self.__request_mode == eRequestType.kGet:
            self.__curl_context.setopt(pycurl.HEADERFUNCTION, self.OnResponseHeaders)
            self.__curl_context.setopt(pycurl.WRITEFUNCTION, self.OnResponseContent)
        elif self.__request_mode == eRequestType.kPost:
            self.__curl_context.setopt(pycurl.POST, 1)
            self.__curl_context.setopt(pycurl.POSTFIELDS, self.__post_fields)
            self.__curl_context.setopt(pycurl.POSTFIELDSIZE, len(self.__post_fields))
            self.__curl_context.setopt(pycurl.HEADERFUNCTION, self.OnResponseHeaders)
            self.__curl_context.setopt(pycurl.WRITEFUNCTION, self.OnResponseContent)
        else:
            return -2
        if self.__proxy_flag == 1:
            self.__curl_context.setopt(pycurl.PROXY, self.__proxy_address + ":" + str(self.__proxy_port));

        if self.__allow_redirect == 0:
            self.__curl_context.setopt(pycurl.FOLLOWLOCATION, 0)
        else:
            self.__curl_context.setopt(pycurl.FOLLOWLOCATION, 1)

        self.__curl_context.setopt(pycurl.CONNECTTIMEOUT, 50)
        self.__curl_context.setopt(pycurl.TIMEOUT, 3000)
        self.__curl_context.setopt(pycurl.FOLLOWLOCATION, 1)
        self.__curl_context.setopt(pycurl.CAINFO,certifi.where())
        self.__curl_context.perform()
        return self.__curl_context.getinfo(pycurl.HTTP_CODE)