import os
import logging
import json
import psycopg

def pgsql_data_read(dsn, query, parameters=None):
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
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                data = []
                for row in rows:
                    data.append(row[0])
            return data
        except Exception as e:
            logger = logging.getLogger('data_manipulation')
            logger.critical(e.args[0])
            return False
        finally:
            if not cursor.closed: cursor.close()
            if not connection.closed: connection.close()
    except Exception as e:
        logger = logging.getLogger('data_manipulation')
        logger.critical(e.args[0])
        return False

def pgsql_data_write(dsn, query, parameters=None):
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
            cursor.execute(query, parameters)
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            logger = logging.getLogger('data_manipulation')
            logger.critical(e.args[0])
            return False
        finally:
            if not cursor.closed: cursor.close()
            if not connection.closed: connection.close()
    except Exception as e:
        logger = logging.getLogger('data_manipulation')
        logger.critical(e.args[0])
        return False
