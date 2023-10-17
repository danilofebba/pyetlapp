import os
import logging
import datetime
import dateutil.tz
import json
import psycopg

def pgsql_db_creation(dsn, parameters):
    try:
        connection = psycopg.connect(
            host = dsn['host'],
            port = dsn['port'],
            dbname = dsn['dbname'],
            user = dsn['user'],
            password = dsn['password']
        )
        cursor = connection.cursor()
        try:
            cursor.execute('''
                create table if not exists public.tb_data_sources (
                    id       serial            not null,
                    name     character varying not null,
                    type     character varying not null,
                    metadata jsonb             not null,
                    constraint uq_data_sources unique (name)
                )
            ''')
            connection.commit()
            cursor.execute('''
                create table if not exists public.tb_objects (
                    id                            serial                      not null,
                    data_source_id                integer                     not null,
                    name                          character varying           not null,
                    extraction_start              timestamp without time zone not null,
                    extraction_end                timestamp without time zone not null,
                    extraction_interval           integer                     not null,
                    extraction_period             integer                     not null,
                    extraction_timezone           character varying           not null,
                    number_of_extraction_attempts integer                     not null,
                    data_file_format              character varying           not null,
                    data_file_schema              character varying               null,
                    storage                       jsonb                       not null,
                    metadata                      jsonb                       not null,
                    constraint uq_objects unique (name)
                )
            ''')
            connection.commit()
            cursor.execute('''
            create table if not exists public.tb_batches (
                id                            bigserial                   not null,
                object_id                     integer                     not null,
                extraction_datetime           timestamp without time zone not null,
                metadata                      jsonb                       not null,
                extraction_status             smallint                    not null default 0,
                number_of_extraction_attempts smallint                    not null default 0,
                extraction_metrics            jsonb                           null
            )
            ''')
            connection.commit()
            for parameter in parameters:
                cursor.execute(
                    '''
                        insert into public.tb_data_sources(name, type, metadata)
                            values(%s, %s, %s)
                        on conflict(name)
                        do update set metadata = excluded.metadata
                    ''', (
                        parameter['name'],
                        parameter['type'],
                        json.dumps(parameter['metadata'])
                    )
                )
                connection.commit()
                cursor.execute('''select id from tb_data_sources where name = %s''', (parameter['name'],))
                data_source_id = cursor.fetchall()
                if data_source_id:
                    for object in parameter['objects']:
                        cursor.execute(
                            '''
                                insert into tb_objects(data_source_id, name, extraction_start, extraction_end, extraction_interval, extraction_period, extraction_timezone, number_of_extraction_attempts, data_file_format, data_file_schema, storage, metadata)
                                values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                on conflict(name)
                                do update set extraction_start              = excluded.extraction_start
                                            , extraction_end                = excluded.extraction_end
                                            , extraction_interval           = excluded.extraction_interval
                                            , extraction_period             = excluded.extraction_period
                                            , extraction_timezone           = excluded.extraction_timezone
                                            , number_of_extraction_attempts = excluded.number_of_extraction_attempts
                                            , data_file_format              = excluded.data_file_format
                                            , data_file_schema              = excluded.data_file_schema
                                            , storage                       = excluded.storage
                                            , metadata                      = excluded.metadata
                            ''', (
                                data_source_id[0][0],
                                object['name'],
                                object['extraction_start'],
                                object['extraction_end'],
                                object['extraction_interval'],
                                object['extraction_period'],
                                object['extraction_timezone'],
                                object['number_of_extraction_attempts'],
                                object['data_file_format'],
                                object['data_file_schema'] if object['data_file_schema'] else None,
                                json.dumps(object['storage']),
                                json.dumps(object['metadata'])
                            )
                        )
                        connection.commit()
            cursor.execute('''
                with objects as (
                        select o.id
                             , o.name
                             , o.extraction_start
                             , o.extraction_end
                             , o.extraction_interval
                             , o.extraction_period
                             , o.extraction_timezone
                             , o.storage
                          from tb_objects as o
                ), batches as (
                        select b.object_id
                             , max(b.extraction_datetime) as extraction_datetime
                          from tb_batches as b
                      group by b.object_id
                )
                        select json_build_object(
                                   'id', objects.id,
                                   'name', objects.name,
                                   'extraction_start', case when batches.extraction_datetime is not null then batches.extraction_datetime + (objects.extraction_interval || ' second')::interval else objects.extraction_start end,
                                   'extraction_end', objects.extraction_end,
                                   'extraction_interval', objects.extraction_interval,
                                   'extraction_period', objects.extraction_period,
                                   'extraction_timezone', objects.extraction_timezone,
                                   'bucket', objects.storage -> 'bucket',
                                   'object_path', objects.storage -> 'object_path'
                               ) as data
                          from objects
                     left join batches on objects.id = batches.object_id
            ''')
            objects = []
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    objects.append(row[0])
            if objects:
                for object in objects:
                    extraction_start = datetime.datetime.strptime(object['extraction_start'], '%Y-%m-%dT%H:%M:%S')
                    extraction_end = datetime.datetime.strptime(object['extraction_end'], '%Y-%m-%dT%H:%M:%S')
                    while extraction_start <= datetime.datetime.now() - datetime.timedelta(seconds=object['extraction_interval']) and extraction_start <= extraction_end - datetime.timedelta(seconds=object['extraction_interval']):
                        for i in range(object['extraction_period']):
                            dti = extraction_start.astimezone(dateutil.tz.gettz(object['extraction_timezone'])) - datetime.timedelta(seconds=object['extraction_interval'] * i)
                            dtf = (extraction_start.astimezone(dateutil.tz.gettz(object['extraction_timezone'])) + datetime.timedelta(seconds=object['extraction_interval'])) - datetime.timedelta(seconds=object['extraction_interval'] * i)
                            if object['object_path']:
                                storage_path = os.path.join(object['bucket'], *object['object_path'], object['name'])
                            else:
                                storage_path = os.path.join(object['bucket'], object['name'])
                            ########################################### variable ###########################################
                            metadata = {
                                'parameters': {
                                    'datetime': {
                                        'start': dti.strftime('%Y-%m-%d %H:%M:%S'),
                                        'end': dtf.strftime('%Y-%m-%d %H:%M:%S')
                                    },
                                    'storage_path': storage_path
                                }
                            }
                            ################################################################################################
                            cursor.execute(
                                '''
                                    insert into tb_batches(object_id, extraction_datetime, metadata)
                                        values(%s, %s, %s)
                                ''', (
                                    object['id'],
                                    extraction_start,
                                    json.dumps(metadata)
                                )
                            )
                        extraction_start += datetime.timedelta(seconds=object['extraction_interval'])
                    connection.commit()
                cursor.execute('''
                    delete from public.tb_batches where id in (
                            select id
                              from (select b.id
                                         , b.object_id
                                         , b.extraction_datetime
                                         , b.metadata #>> '{parameters, datetime, start}' as start_datetime
                                         , row_number() over (partition by b.object_id, b.metadata #>> '{parameters, datetime, start}' order by b.object_id, b.extraction_datetime, b.metadata #>> '{parameters, datetime, start}') as delete_flag
                                      from public.tb_batches as b
                                     where b.extraction_status = 0) as stmt1
                             where delete_flag > 1
                             union all
                            select b.id
                              from public.tb_batches as b
                        inner join public.tb_objects as o
                                on b.object_id = o.id
                             where b.extraction_status = 0
                               and (b.metadata #>> '{parameters, datetime, start}')::timestamp < o.extraction_start
                    )
                ''')
                connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            logger = logging.getLogger('pgsql_db_creation')
            logger.critical(e.args[0])
            return False
        finally:
            if not cursor.closed: cursor.close()
            if not connection.closed: connection.close()
    except Exception as e:
        logger = logging.getLogger('pgsql_db_creation')
        logger.critical(e.args[0])
        return False
