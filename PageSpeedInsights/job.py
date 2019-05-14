#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights Job + Google Cloud Functions'''
import os
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TOPIC_NAME = "psi-single"

URL_DICT = ["https://m.ctrip.com/webapp/flight/schedule/detail.html"]

def run(event, context):
    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
    for url in URL_DICT:
        data = url.encode('utf-8')
        publisher.publish(topic, data)
    return 'OK'

def test_job():
    print('TODO')

if __name__ == "__main__":
    test_job()
