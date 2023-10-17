import io
import os
import json
import uuid
import random
import datetime
import time
from dateutil.relativedelta import relativedelta
import psycopg

os.environ["ADMIN_HOSTNAME"] = "192.168.0.10"
os.environ["ADMIN_PORT"] = "5432"
os.environ["ADMIN_DATABASE"] = "db_01"
os.environ["ADMIN_USER"] = "user_01"
os.environ["ADMIN_PASSWORD"] = "123456"

while True:
    try:
        conn = psycopg.connect(
            host=os.environ["ADMIN_HOSTNAME"],
            port=os.environ["ADMIN_PORT"],
            dbname=os.environ["ADMIN_DATABASE"],
            user=os.environ["ADMIN_USER"],
            password=os.environ["ADMIN_PASSWORD"],
            autocommit = True
        )
        cur = conn.cursor()
        break
    except:
        time.sleep(10)

cur.execute("""
    create table if not exists public.tb_01(
        id          uuid,
        code        integer,
        option      character(8),
        description character varying(24),
        value       double precision,
        rate        double precision,
        created_at  timestamp without time zone,
        updated_at  timestamp without time zone,
        status      boolean
    )
""")

interval_start = 1696118400000000 #int(time.mktime((datetime.datetime(datetime.datetime.now().year,1,1) - relativedelta(years=1)).timetuple()) * 1000000)
interval_end = 1698796800000000 - 1 #int(time.mktime((datetime.datetime(datetime.datetime.now().year,1,1) + relativedelta(years=2)).timetuple()) * 1000000) - 1

data = []
n = 100000000
l = 0
for i in range(1, n):
    dt = datetime.datetime.fromtimestamp(random.randint(interval_start, interval_end) / 1000000)
    data.append(
        (
            uuid.uuid4(),
            i,
            "option {0}".format(random.randint(1,5)),
            "description {0}".format(i),
            random.gauss(400, 50),
            random.random(),
            dt,
            dt,
            True if random.randint(0,1) == 1 else False
        )
    )
    l += 1
    if l == 1000000 or i == n - 1:
        with cur.copy("COPY public.tb_01 FROM STDIN") as copy:
            for record in data:
                copy.write_row(record)
        data = []
        l = 0

#cur.execute('create index if not exists idx_01 on public.tb_01 using btree (updated_at)')

cur.close()
conn.close()
