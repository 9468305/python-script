#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import psi
import job

def psi_pubsub(event, context):
    psi.run_pubsub(event, context)

def job_pubsub(event, context):
    job.run(event, context)
