#!/usr/bin/env python
# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express
# or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""
Demonstrates how to use an ML Model, by setting the score threshold,
and kicks off a batch prediction job, which uses the ML Model to
generate predictions on new data.  This script needs the id of the
ML Model to use.  It also requires the score threshold.
Useage:
    python use_model.py ml_model_id score_threshold s3_output_url
For example:
    python use_model.py ml-12345678901 0.77 s3://your-bucket/prefix

"""
#datos: https://s3.amazonaws.com/predictions/prueba_ML_model.ods
#id modelo: ml-aCkdtmsoadc
#resultado: https://s3.amazonaws.com/predictions/resultado
#ejemplo: python using_machine_learning.py ml-aCkdtmsoadc 0.77 s3://predictions



import base64
import boto3
import datetime
import os
import random
import sys
import time
import urlparse

import boto
import json
import datetime

from boto.s3.key import Key

# The URL of the sample data in S3
now = datetime.datetime.now()
dia = now.day
mes= now.month
ano = now.year

datos = 'Datos para ML del ' +str(dia)+'-'+ str(mes)+'-'+str(ano)
#UNSCORED_DATA_S3_URL = "s3://predictions/prueba_ML_model.csv"
UNSCORED_DATA_S3_URL = "s3://predictions/" + datos + '.csv'

with open('../aws_apikey', 'r') as f:
    AWS_ACCESS_KEY_ID = f.read()
    AWS_SECRET_ACCESS_KEY = f.read()

f.closed
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID.rstrip()
AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY.rstrip()

def use_model(model_id, threshold, schema_fn, output_s3, data_s3url):
    """Creates all the objects needed to build an ML Model & evaluate its quality.
    """
    ml = boto3.client('machinelearning',region_name='us-east-1',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    #ml = boto3.client('machinelearning',region_name='us-east-1')
    poll_until_completed(ml, model_id)  # Can't use it until it's COMPLETED
    #ml.update_ml_model(MLModelId=model_id, ScoreThreshold=threshold)
    ml.update_ml_model(MLModelId=model_id)
    print("Set score threshold for %s to %.2f" % (model_id, threshold))

    bp_id = 'bp-' + base64.b32encode(os.urandom(10))
    ds_id = create_data_source_for_scoring(ml, data_s3url, schema_fn)
    ml.create_batch_prediction(
        BatchPredictionId=bp_id,
        BatchPredictionName="Batch Prediction for marketing sample",
        MLModelId=model_id,
        BatchPredictionDataSourceId=ds_id,
        OutputUri=output_s3
    )
    print("Created Batch Prediction %s" % bp_id)
    poll_until_completed2(bp_id, 'bp')
    return bp_id


def poll_until_completed(ml, model_id):
    delay = 2
    while True:
        model = ml.get_ml_model(MLModelId=model_id)
        status = model['Status']
        message = model.get('Message', '')
        now = str(datetime.datetime.now().time())
        print("Model %s is %s (%s) at %s" % (model_id, status, message, now))
        if status in ['COMPLETED', 'FAILED', 'INVALID']:
            break

        # exponential backoff with jitter
        delay *= random.uniform(1.1, 2.0)
        time.sleep(delay)


def create_data_source_for_scoring(ml, data_s3url, schema_fn):
    ds_id = 'ds-' + base64.b32encode(os.urandom(10))
    ml.create_data_source_from_s3(
        DataSourceId=ds_id,
        DataSourceName="DS for Batch Prediction %s" % data_s3url,
        DataSpec={
            "DataLocationS3": data_s3url,
            "DataSchema": open(schema_fn).read(),
        },
        ComputeStatistics=False
    )
    print("Created Datasource %s for batch prediction" % ds_id)
    return ds_id

def poll_until_completed2(entity_id, entity_type_str):
    ml = boto.connect_machinelearning(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    polling_function = {
        'ds': ml.get_data_source,
        'ml': ml.get_ml_model,
        'ev': ml.get_evaluation,
        'bp': ml.get_batch_prediction,
    }[entity_type_str]
    delay = 2
    while True:
        results = polling_function(entity_id)
        status = results['Status']
        message = results.get('Message', '')
        now = str(datetime.datetime.now().time())
        print("Object %s is %s (%s) at %s" % (entity_id, status, message, now))
        if status in ['COMPLETED', 'FAILED', 'INVALID']:
            break

        # exponential backoff with jitter
        delay *= random.uniform(1.1, 2.0)
        time.sleep(delay)
    print(json.dumps(results, indent=2))

def download(bucket, filename,bp_id):
    key = Key(bucket, filename)
    headers = {}
    mode = 'wb'
    updating = False
    if os.path.isfile(filename):
        mode = 'r+b'
        updating = True
        print "File exists, adding If-Modified-Since header"
        modified_since = os.path.getmtime(filename)
        timestamp = datetime.datetime.utcfromtimestamp(modified_since)
        headers['If-Modified-Since'] = timestamp.strftime("%a, %d %b %Y %H:%M:%S GMT")
    try:
        #with open(filename, mode) as f:
        with open("%s.csv.gz" % bp_id, mode) as f:
            key.get_contents_to_file(f, headers)
            f.truncate()
    except boto.exception.S3ResponseError as e:
        if not updating:
            # got an error and we are not updating an existing file
            # delete the file that was created due to mode = 'wb'
            os.remove(filename)
        return e.status
    return 200

if __name__ == "__main__":
    try:
        model_id = sys.argv[1]
        threshold = float(sys.argv[2])
        s3_output_url = sys.argv[3]
        parsed_url = urlparse.urlparse(s3_output_url)
        if parsed_url.scheme != 's3':
            raise RuntimeError("s3_output_url must be an s3:// url")
    except IndexError:
        print(__doc__)
        sys.exit(-1)
    except:
        print(__doc__)
        raise
    bp_id = use_model(model_id, threshold, "demanda.csv.schema",
              s3_output_url, UNSCORED_DATA_S3_URL)

    bucket_name = 'predictions'
    conn = boto.connect_s3(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)
    descarga = 'batch-prediction/result/'+bp_id + '-' + datos +'.csv.gz'
    print download(bucket, descarga,bp_id+ '-' + datos)
    #print download(bucket, 'batch-prediction/result/%s-%s.gz' % bp_id % datos,bp_id)
