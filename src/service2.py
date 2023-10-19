import subprocess
import json

batch1 = json.dumps({"dsn":  {"host": "192.168.0.10", "port": "5432", "dbname": "db_01"}, "query": "select id, code, option, description, value, rate, created_at, updated_at, status, to_char(updated_at, 'YYYY-MM-DD') as date from public.tb_01 where updated_at >= '%(start)s' and updated_at < '%(end)s'", "parameters":  {"end": "2023-10-02 00:00:00", "start": "2023-10-01 00:00:00"}, "array_size": 1000000, "data_file_format": "parquet", "partition_by": ["date"], "storage_path": "s3a://ddfs-bucket-01/group/company/db_01_public_tb_01", "object_name": "db_01_public_tb_01", "batch_id": 2})
batch2 = json.dumps({"dsn":  {"host": "192.168.0.10", "port": "5432", "dbname": "db_01"}, "query": "select id, code, option, description, value, rate, created_at, updated_at, status, to_char(updated_at, 'YYYY-MM-DD') as date from public.tb_01 where updated_at >= '%(start)s' and updated_at < '%(end)s'", "parameters":  {"end": "2023-10-03 00:00:00", "start": "2023-10-02 00:00:00"}, "array_size": 1000000, "data_file_format": "parquet", "partition_by": ["date"], "storage_path": "s3a://ddfs-bucket-01/group/company/db_01_public_tb_02", "object_name": "db_01_public_tb_02", "batch_id": 3})
batch3 = json.dumps({"dsn":  {"host": "192.168.0.10", "port": "5432", "dbname": "db_01"}, "query": "select id, code, option, description, value, rate, created_at, updated_at, status, to_char(updated_at, 'YYYY-MM-DD') as date from public.tb_01 where updated_at >= '%(start)s' and updated_at < '%(end)s'", "parameters":  {"end": "2023-10-04 00:00:00", "start": "2023-10-03 00:00:00"}, "array_size": 1000000, "data_file_format": "parquet", "partition_by": ["date"], "storage_path": "s3a://ddfs-bucket-01/group/company/db_01_public_tb_03", "object_name": "db_01_public_tb_03", "batch_id": 4})

proc1 = subprocess.Popen(['spark-submit', 'service1.py', '-b', batch1])
proc2 = subprocess.Popen(['spark-submit', 'service1.py', '-b', batch2])
proc3 = subprocess.Popen(['spark-submit', 'service1.py', '-b', batch3])

proc1.wait()
proc2.wait()
proc3.wait()
