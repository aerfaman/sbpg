import requests
import re
import json
from getToken import getToken

class getuserinfo:
    def __init__(self, apitoken):
        self.apitoken=apitoken
        self.geturl=r'https://api.shanbay.com/account/'
        self.postheaders={
            "Authorization":"Bearer %s"%self.apitoken,
            'content-type': "application/json",
        }

    def get(self):
        getstatus={}
        r=requests.session()
        s=r.get(self.geturl,headers=self.postheaders)
        if "username" in json.loads(s.text).keys():
            getstatus['status']=0
            getstatus['message']="success"
            getstatus['data']=json.loads(s.text)
        else:
            getstatus['status']=1
            getstatus['message']="Wrong token"

        return getstatus