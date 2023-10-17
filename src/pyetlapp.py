import os
import time
import json
import logging

import config.parameters
import lib.batches_control
import lib.data_manipulation

import findspark
findspark.init()
from pyspark.sql import SparkSession

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%y/%m/%d %H:%M:%S',
    level=logging.INFO 
)

def execute_batches_extraction(dsn):
    batches = lib.data_manipulation.pgsql_data_read(
        dsn=dsn,
        query="""
                select json_build_object(
                           'dsn', ds.metadata -> 'dsn',
                           'query', o.metadata -> 'query',
                           'parameters', b.metadata -> 'parameters' -> 'datetime',
                           'array_size', o.metadata -> 'array_size',
                           'data_file_format', o.data_file_format,
                           'partition_by', o.metadata -> 'partition_by',
                           'storage_path', b.metadata -> 'parameters' -> 'storage_path',
                           'object_name', o.name,
                           'batch_id', b.id
                       ) as batches
                  from tb_data_sources as ds
            inner join tb_objects as o
                    on ds.id = o.data_source_id
            inner join tb_batches as b
                    on o.id = b.object_id
                 where ds.type = 'database'
                   and b.extraction_status = 0
                   and b.number_of_extraction_attempts < o.number_of_extraction_attempts
                   and b.extraction_datetime <= current_timestamp at time zone 'America/Sao_Paulo' - (o.extraction_interval::text || ' second')::interval
              order by b.extraction_datetime asc
                     , o.id asc
        """
    )
    if batches:
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
        for batch in batches:
            t = time.time()
            df = spark.read \
                .format("jdbc") \
                .option("driver", "org.postgresql.Driver") \
                .option("url", f"jdbc:postgresql://{batch['dsn']['host']}:{batch['dsn']['port']}/{batch['dsn']['dbname']}") \
                .option("user", os.environ['DATA_SOURCE_USER']) \
                .option("password", os.environ['DATA_SOURCE_PASSWORD']) \
                .option("dbtable", f"({batch['query']%batch['parameters']}) as query") \
                .option("fetchsize", batch['array_size']) \
                .load()
            extracted_rows = df.count()
            extraction_time = round(time.time() - t, 3)
            t = time.time()
            df.write \
                .format(batch['data_file_format']) \
                .option('compression', 'gzip') \
                .partitionBy(batch['partition_by']) \
                .mode('append') \
                .save(batch['storage_path'])
            load_time = round(time.time() - t, 3)
            lib.data_manipulation.pgsql_data_write(
                dsn=dsn,
                query="""
                    update tb_batches
                       set extraction_status = %s
                         , number_of_extraction_attempts = (select number_of_extraction_attempts from tb_batches where id = %s) + 1
                         , extraction_metrics = %s
                     where id = %s
                """,
                parameters=(
                    1,
                    batch['batch_id'],
                    json.dumps({'extracted_rows': extracted_rows, 'extraction_time': extraction_time, 'load_time': load_time}),
                    batch['batch_id']
                )
            )
        spark.stop()
        del spark

if __name__ == '__main__':
    dsn = {
        "host": os.environ['PYETLDB_HOST'],
        "port": os.environ['PYETLDB_PORT'],
        "dbname": os.environ['PYETLDB_DBNAME'],
        "user": os.environ['PYETLDB_USER'],
        "password": os.environ['PYETLDB_PASSWORD']
    }
    parameters = lib.batches_control.pgsql_db_creation(dsn=dsn, parameters=config.parameters.data_sources)
    if parameters:
        execute_batches_extraction(dsn)
