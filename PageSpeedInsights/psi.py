#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights Single + Google Cloud Functions'''
import os
import base64
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
                   "locale": "zh-CN",
                   "strategy": "mobile",
                   "key": API_KEY
                   }
        response = SESSION.get(url=GAPI_PSI, params=payload, proxies=PROXIES)
        print(response.status_code)
        print(response.json())
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
    PROXIES = {
        "http": "127.0.0.1:1087",
        "https": "127.0.0.1:1087",
    }

    _test_url = "https://m.ctrip.com/webapp/flight/schedule/detail.html"
    test_run_http(_test_url)
    test_run_pubsub(_test_url)


"""
from google.cloud import storage
client = storage.Client()
# https://console.cloud.google.com/storage/browser/[bucket-id]/
bucket = client.get_bucket('bucket-id-here')
# Then do other things...
blob = bucket.get_blob('remote/path/to/file.txt')
print(blob.download_as_string())
blob.upload_from_string('New contents!')
blob2 = bucket.blob('remote/path/storage.txt')
blob2.upload_from_filename(filename='/local/path.txt')
"""