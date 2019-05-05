#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
PageSpeed Insights + Google Cloud Functions
'''

from googleapiclient.discovery import build
import setting

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'

def run(request):
    '''
    Call PageSpeedInsights API
    '''
    service = build(serviceName='pagespeedonline', version='v5', developerKey=setting.API_KEY)
    print('\n'.join(['%s:%s' % item for item in service.__dict__.items()]))


if __name__ == "__main__":
    run("")
