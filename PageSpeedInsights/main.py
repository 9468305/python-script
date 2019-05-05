#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights + Google Cloud Functions'''
import os
from googleapiclient.discovery import build

# Access Token, generated from GCP Console Credentials page.
API_KEY = os.getenv('GCP_API_KEY')

# For local development, setup http proxy as needed.
HTTP = None

def run(request):
    '''Run PageSpeedInsights API'''
    request_json = request.get_json()
    try:
        url = request_json['url']
    except KeyError:
        return ('', 400)

    pagespeedonline = build(
        serviceName = 'pagespeedonline',
        version = 'v5',
        http = HTTP,
        developerKey = API_KEY
    )
    response = pagespeedonline.pagespeedapi().runpagespeed(
        url = url
    ).execute()
    print(response)
    return ('OK', 200)

if __name__ == "__main__":
    from flask import Request
    _request = Request.from_values(
        json = { "url": "https://m.ctrip.com" }
    )

    import httplib2
    HTTP = httplib2.Http(
        proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1086)
    )

    run(_request)
