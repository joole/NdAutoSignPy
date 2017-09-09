#!/usr/bin/python
# -*- coding: UTF-8 -*-
#coding=utf-8 

import hashlib
import random
import binascii
import base64
import hmac
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class NdCalculateUtil():
    """
    产生长度为count的随机字符串
    """
    def generateMixRandomCode(self,count):
        base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = []
        #count = len(base)
        for index in range(count):
            result.append(base[random.randint(0, len(base)-1)])
        return "".join(result)
        

    def encryptHMac256(self,rawmac, mackey):
        message = bytes(rawmac).encode('utf-8')
        secret = bytes(mackey).encode('utf-8')
        signature = base64.b64encode(hmac.new(secret,message, digestmod=hashlib.sha256).digest())    
        return signature

    def md5Encrypt(self,src):
        #salt_byte_arr = bytearray(b'\xa3\xac\xa1\xa3\x66\x64\x6a\x66\x2c\x6a\x6b\x67\x66\x6b\x6c')  
        code = sys.getdefaultencoding()
        salt_str = b'\xa3\xac\xa1\xa3fdjf,jkgfkl'       
        hash = hashlib.md5()

        hash.update(src + salt_str)
        return hash.hexdigest()
        

    def base64Encode(self,src):
        pass

    def hMacEncode(algo, key, input):
        pass
    
    