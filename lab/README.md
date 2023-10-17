```bash
/opt/spark/sbin/start-master.sh
/opt/spark/sbin/start-worker.sh spark://spark-master:7077 --cores 2 --memory 2g
/opt/spark/bin/spark-submit test_01.py
/opt/spark/bin/spark-submit test_02.py
```
