import os
import time
import json
import uuid
import boto3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--batch', dest='batch', help='batch')
batch = json.loads(parser.parse_args().batch)

import findspark
findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .config('spark.jars', '/opt/spark/jars/aws-java-sdk-bundle-1.12.505.jar,/opt/spark/jars/hadoop-aws-3.3.4.jar,/opt/spark/jars/hadoop-common-3.3.4.jar,/opt/spark/jars/postgresql-42.6.0.jar') \
    .config('spark.master', 'spark://192.168.0.30:7077') \
    .config('spark.cores.max', 2) \
    .config('spark.executor.cores', 2) \
    .config('spark.executor.memory', '2g') \
    .config('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem') \
    .config('spark.hadoop.fs.s3a.endpoint', os.environ['STORAGE_ENDPOINT']) \
    .config('spark.hadoop.fs.s3a.access.key', os.environ['AWS_ACCESS_KEY_ID']) \
    .config('spark.hadoop.fs.s3a.secret.key', os.environ['AWS_SECRET_ACCESS_KEY']) \
    .getOrCreate()

t = time.time()
df = spark.read \
    .format('jdbc') \
    .option('driver', 'org.postgresql.Driver') \
    .option('url', f"jdbc:postgresql://{batch['dsn']['host']}:{batch['dsn']['port']}/{batch['dsn']['dbname']}") \
    .option('user', os.environ['DATA_SOURCE_USER']) \
    .option('password', os.environ['DATA_SOURCE_PASSWORD']) \
    .option('dbtable', f"({batch['query']%batch['parameters']}) as query") \
    .option('fetchsize', batch['array_size']) \
    .load()
extracted_rows = df.count()
extraction_time = round(time.time() - t, 3)

t = time.time()
path_id = str(uuid.uuid4())
df.write \
    .format(batch['data_file_format']) \
    .option('compression', 'gzip') \
    .partitionBy(batch['partition_by']) \
    .mode('append') \
    .save(os.path.join(batch['storage_path'], path_id))
s3 = boto3.resource(
    's3',
    endpoint_url = os.environ['STORAGE_ENDPOINT'],
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
)
bucket = s3.Bucket(batch['bucket'])
for object in bucket.objects.filter(Prefix=os.path.join(batch['prefix_path'], path_id)):
    if object.key != os.path.join(batch['prefix_path'], path_id, '_SUCCESS'):
        s3.Object(
            bucket_name = batch['bucket'],
            key = object.key.replace(f'{path_id}/', '')
        ).copy_from(
            CopySource=os.path.join(object.bucket_name, object.key)
        )
    object.delete()
load_time = round(time.time() - t, 3)

spark.stop()
del spark
