#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''PageSpeed Insights Job + Google Cloud Functions'''
import os
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TOPIC_NAME = os.getenv("GCP_TOPIC_NAME")

def run(event, context):
    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
    data = None
    publisher.publish(topic, data)

    print('Topic created: {}'.format(topic))
    return 'OK'

def test_job():
    print()

if __name__ == "__main__":
    test_job()
