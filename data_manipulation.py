import os
import logging
import json
import sqlite3
import psycopg2


def pgsql_data_read(dsn, query, parameters=None):
    try:
        connection = psycopg2.connect(
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
        connection = psycopg2.connect(
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
            logger.info(cursor.query) ###########################tirar
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




def write_data(query, parameters=None):
    database = os.path.join(os.getcwd(), 'pyetldb.db')
    if os.path.exists(database):
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            cursor.execute(query, parameters)
            connection.commit()
            return True
        except sqlite3.Error as e:
            logger = logging.getLogger('sqlitedb')
            logger.critical(e.args[0])
            return False
        finally:
            cursor.close()
            connection.close()
    else:
        logger = logging.getLogger('sqlitedb')
        logger.critical('The pyetldb.db file does not exist!')
        return False

def read_data(query, parameters=None):
    database = os.path.join(os.getcwd(), 'pyetldb.db')
    if os.path.exists(database):
        try:
            connection = sqlite3.connect(database)
            cursor = connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            data = []
            while True:
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        data.append(json.loads(row[0]))
                    return data
                else:
                    break
        except sqlite3.Error as e:
            logger = logging.getLogger('sqlitedb')
            logger.critical(e.args[0])
            return False
        finally:
            cursor.close()
            connection.close()
    else:
        logger = logging.getLogger('sqlitedb')
        logger.critical('The pyetldb.db file does not exist!')
        return False