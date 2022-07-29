data_sources = [
    {
        "name": "my_application",
        "type": "database",
        "metadata": {
            "dbms": "pgsql;",
            "dsn": {
                "host": "my_instance.xxxxxxxxxxxxxxx.us-east-1.rds.amazonaws.com",
                "port": "5432",
                "dbname": "my_database"
            },
            "maximum_number_of_parallel_connections": "1"
        },
        "objects": [
            {
                "name": "my_database_schema_table",
                "extraction_start": "2022-07-01 00:00:00",
                "extraction_end": "9999-12-31 23:59:59",
                "extraction_interval": 21600,
                "extraction_period": 1,
                "extraction_timezone": "UTC",
                "number_of_extraction_attempts": 3,
                "data_file_format": "parquet",
                "data_file_schema": None,
                "storage": {
                    "bucket": "my_bucket",
                    "object_path": ['my', 'path']
                },
                "metadata": {
                    "array_size": 10000,
                    "query": """
                        select t.id
                             , t.field2
                             , t.field3
                             , t.created_at
                             , t.updated_at
                             , to_char(t.updated_at, 'YYYY') as year
                             , to_char(t.updated_at, 'MM') as month
                             , to_char(t.updated_at, 'DD') as day
                          from public.my_table as t
                         where t.updated_at >= '%(start)s' and t.updated_at < '%(end)s'
                    """,
                    "partition_by": ['year', 'month', 'day']
                }
            }
        ]
    }
]