#!/usr/bin/env python3
# -*- coding: utf-8 -*-'
import json
import requests

localheaders = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}
start_url = 'https://www.douyu.com//8832994'

response = requests.get( start_url, headers=localheaders)
print(json.loads(response.content.decode()))