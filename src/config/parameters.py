data_sources = [
    {
        "name": "my_application",
        "type": "database",
        "metadata": {
            "dbms": "pgsql;",
            "dsn": {
                "host": "192.168.0.10",
                "port": "5432",
                "dbname": "db_01"
            },
            "maximum_number_of_parallel_connections": "1"
        },
        "objects": [
            {
                "name": "db_01_public_tb_01",
                "extraction_start": "2023-10-01 00:00:00",
                "extraction_end": "9999-12-31 23:59:59",
                "extraction_interval": 86400,
                "extraction_period": 1,
                "extraction_timezone": "UTC",
                "number_of_extraction_attempts": 3,
                "data_file_format": "parquet",
                "data_file_schema": None,
                "storage": {
                    "uri_scheme": "s3a",
                    "bucket": "ddfs-bucket-01",
                    "object_path": {"group": "my_group", "company": "my_company"}
                },
                "metadata": {
                    "array_size": 1000000,
                    "query": """
                        select id
                             , code
                             , option
                             , description
                             , value
                             , rate
                             , created_at
                             , updated_at
                             , status
                             , to_char(updated_at, 'YYYY-MM-DD') as date
                          from public.tb_01
                         where updated_at >= '%(start)s' and updated_at < '%(end)s'
                    """,
                    "partition_by": ["date"]
                }
            }
        ]
    }
]
