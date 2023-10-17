import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%y/%m/%d %H:%M:%S',
    level=logging.INFO 
)

import uuid
import random
import datetime
import time
from dateutil.relativedelta import relativedelta

interval_start = int(time.mktime((datetime.datetime(datetime.datetime.now().year,1,1) - relativedelta(years=1)).timetuple()) * 1000000)
interval_end = int(time.mktime((datetime.datetime(datetime.datetime.now().year,1,1) + relativedelta(years=2)).timetuple()) * 1000000) - 1
data = []
l = 0
for i in range(0, 1000000):
    dt = datetime.datetime.fromtimestamp(random.randint(interval_start, interval_end) / 1000000)
    data.append(
        {
            "id": str(uuid.uuid4()),
            "code": i,
            "option": "option {0}".format(random.randint(1,5)),
            "description": "description {0}".format(i),
            "value": random.gauss(400, 50),
            "rate": random.random(),
            "created_at": dt,
            "updated_at": dt,
            "status": True if random.randint(0,1) == 1 else False,
            "date": dt.date()
        }
    )
    l += 1

import json

import findspark
findspark.init()
from pyspark.sql.types import *

schema = StructType.fromJson(
    json.loads('''
        {
            "type": "struct",
            "fields": [
                {
                    "name": "id",
                    "type": "string",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "code",
                    "type": "integer",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "option",
                    "type": "string",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "description",
                    "type": "string",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "value",
                    "type": "double",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "rate",
                    "type": "double",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "created_at",
                    "type": "timestamp_ntz",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "updated_at",
                    "type": "timestamp_ntz",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "status",
                    "type": "boolean",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "date",
                    "type": "date",
                    "nullable": true,
                    "metadata": {}
                }
            ]
        }
    ''')
)

import os
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .config("spark.jars", "/opt/spark/jars/aws-java-sdk-bundle-1.12.505.jar,/opt/spark/jars/hadoop-aws-3.3.4.jar,/opt/spark/jars/hadoop-common-3.3.4.jar") \
    .config('spark.master', 'spark://192.168.0.30:7077') \
    .config("spark.cores.max", 2) \
    .config("spark.executor.cores", 2) \
    .config("spark.executor.memory", "2g") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://192.168.0.20:9000") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ['AWS_ACCESS_KEY_ID']) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ['AWS_SECRET_ACCESS_KEY']) \
    .getOrCreate()

df = spark.createDataFrame(data, schema=schema)

df.write \
    .format('parquet') \
    .option('compression', 'gzip') \
    .partitionBy(['date']) \
    .mode('append') \
    .save('s3a://ddfs-bucket-01/tb_02')

spark.stop()
