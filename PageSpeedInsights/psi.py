#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights Single + Google Cloud Functions'''
import os
import requests

# Access Token, generated from GCP Console Credentials page.
API_KEY = os.getenv('GCP_API_KEY')

GAPI_PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

SESSION = requests.Session()

PROXIES = None


def run(url):
    try:
        payload = {"url": url,
                   "category": "performance",
                   "locale": "zh",
                   "strategy": "mobile",
                   "key": API_KEY
                   }
        response = SESSION.get(url=GAPI_PSI, params=payload, proxies=PROXIES)
        print(response.status_code)
        print(response.json())
    except requests.RequestException as _e:
        print(_e)
    return ('OK', 200)


def run_pubsub(event, context):
    import base64
    pubsub_message = base64.urlsafe_b64decode(event['data']).decode('utf-8')
    run(pubsub_message)
    return 'OK'


def test_run_http(test_url):
    run(test_url)


def test_run_pubsub(test_url):
    import base64
    event = {"data": base64.urlsafe_b64encode(test_url.encode('utf-8'))}
    context = None
    run_pubsub(event, context)


if __name__ == "__main__":
    PROXIES = {
        "http": "127.0.0.1:1087",
        "https": "127.0.0.1:1087",
    }

    _test_url = "https://m.ctrip.com/webapp/flight/schedule/detail.html"
    test_run_http(_test_url)
    test_run_pubsub(_test_url)
