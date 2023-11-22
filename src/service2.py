import os
import json
import subprocess
import concurrent.futures

import lib.data_manipulation

def worker(batch):
    with subprocess.Popen(['spark-submit', 'service1.py', '-b', json.dumps(batch)]) as p:
        p.wait()
    return batch['batch_id']

def main():
    batches = lib.data_manipulation.pgsql_data_read(
        dsn = {
            "host": os.environ['PYETLDB_HOST'],
            "port": os.environ['PYETLDB_PORT'],
            "dbname": os.environ['PYETLDB_DBNAME'],
            "user": os.environ['PYETLDB_USER'],
            "password": os.environ['PYETLDB_PASSWORD']
        },
        query="""
                select json_build_object(
                           'dsn', ds.metadata -> 'dsn',
                           'query', o.metadata -> 'query',
                           'parameters', b.metadata -> 'parameters' -> 'datetime',
                           'array_size', o.metadata -> 'array_size',
                           'data_file_format', o.data_file_format,
                           'batch_id', b.id,
                           'object_name', o.name,
                           'bucket', o."storage" -> 'bucket',
                           'prefix_path', b.metadata -> 'parameters' -> 'prefix_path',
                           'storage_path', b.metadata -> 'parameters' -> 'storage_path',
                           'partition_by', o.metadata -> 'partition_by'
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(worker, batch) for batch in batches]
        for future in concurrent.futures.as_completed(futures):
            try:
                print(future.result())
            except Exception as e:
                print(e)

if __name__ == '__main__':
    main()
