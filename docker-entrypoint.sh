#!/bin/bash
if [[ `hostname` == "pyetlapp" ]]; then
    # python3 /opt/pyetlapp/pyetlapp.py
    ############################################# TMP #############################################
    jupyter notebook --generate-config
    echo -e "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py
    echo -e "c.NotebookApp.password = 'argon2:\$argon2id\$v=19\$m=10240,t=10,p=8\$635AifC1hEtV+BPmOyHphQ\$lP1zV4+cd0BODPyv3IW7h4j/3PKd8cnAgJGoebpsqwA'" >> /root/.jupyter/jupyter_notebook_config.py
    jupyter notebook --ip=0.0.0.0 --allow-root
    ###############################################################################################
else
    if [[ "$INSTANCE" == "MASTER" ]]; then
        /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master
    elif [[ "$INSTANCE" == "WORKER" ]]; then
        /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT
    fi
fi
