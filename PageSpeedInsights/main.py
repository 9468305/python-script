#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights + Google Cloud Functions'''
import os
from googleapiclient.discovery import build

# Access Token, generated from GCP Console Credentials page.
API_KEY = os.getenv('GCP_API_KEY')

# For local development, setup http proxy as needed.
HTTP = None

def run(url):
    pagespeedonline = build(
        serviceName = 'pagespeedonline',
        version = 'v5',
        http = HTTP,
        developerKey = API_KEY
    )
    response = pagespeedonline.pagespeedapi().runpagespeed(url = url).execute()
    print(response)
    return ('OK', 200)

def run_http(request):
    request_json = request.get_json()
    try:
        url = request_json['url']
        return run(url)
    except KeyError:
        return ('', 400)

def run_pubsub(event, context):
    import base64
    pubsub_message = base64.urlsafe_b64decode(event['data']).decode('utf-8')
    run(pubsub_message)
    return 'OK'


if __name__ == "__main__":
    import httplib2
    HTTP = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 1086))

    from flask import Request
    _request = Request.from_values(json = { "url": "https://m.ctrip.com" })
    run_http(_request)

    import base64
    event = { "data": base64.urlsafe_b64encode("https://m.ctrip.com".encode('utf-8'))}
    context = None
    run_pubsub(event, context)
