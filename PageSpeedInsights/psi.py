#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights Single + Google Cloud Functions'''
import os
import base64
import json
from urllib import parse
import requests
from google.cloud import storage
from google.cloud.storage import Blob

# Access Token, generated from GCP Console Credentials page.
API_KEY = os.getenv('GCP_API_KEY')

GAPI_PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

SESSION = requests.Session()

PROXIES = None


def save(url, report):
    '''Save to https://console.cloud.google.com/storage/browser/[bucket-id]/'''
    client = storage.Client()
    bucket = client.get_bucket("psi-report")
    blob = Blob(f"${parse.quote_plus(url)}.json", bucket)
    blob.upload_from_string(report, "application/json")


def run(url):
    try:
        payload = {"url": url,
                   "category": "performance",
                   "locale": "zh-CN",
                   "strategy": "mobile",
                   "key": API_KEY
                   }
        response = SESSION.get(url=GAPI_PSI, params=payload, proxies=PROXIES)
        print(response.status_code)
        if 200 == response.status_code:
            save(url, response.text)
    except requests.RequestException as _e:
        print(_e)
    return 'OK'


def run_pubsub(event, context):
    pubsub_message = base64.urlsafe_b64decode(event['data']).decode('utf-8')
    return run(pubsub_message)


def test_run_http(test_url):
    run(test_url)


def test_run_pubsub(test_url):
    event = {"data": base64.urlsafe_b64encode(test_url.encode('utf-8'))}
    context = None
    run_pubsub(event, context)


if __name__ == "__main__":
    _proxy = os.getenv("HTTP_PROXY")
    PROXIES = {
        "http": _proxy,
        "https": _proxy,
    }
    _test_url = "https://m.ctrip.com/webapp/flight/schedule/detail.html"
    test_run_http(_test_url)
    test_run_pubsub(_test_url)
