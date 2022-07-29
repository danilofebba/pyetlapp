FROM alpine:latest

RUN apk update \
    && apk --no-cache add \
        bash \
        curl \
        openjdk8 \
        python3 \
        python3-dev \
        py3-pip \
        py3-psycopg2 \
        aws-cli \
    && python3 -m pip install --upgrade pip \
        setuptools \
        wheel \
        python-dateutil \
        findspark \
    && curl -s https://archive.apache.org/dist/spark/spark-3.1.3/spark-3.1.3-bin-hadoop3.2.tgz -o /tmp/spark-3.1.3-bin-hadoop3.2.tgz \
    && tar -zxvf /tmp/spark-3.1.3-bin-hadoop3.2.tgz -C /opt \
    && mv /opt/spark-3.1.3-bin-hadoop3.2 /opt/spark \
    && rm /tmp/spark-3.1.3-bin-hadoop3.2.tgz \
    && mkdir -p /opt/pyetlapp/jars \
    && cd /opt/pyetlapp/jars \
    && curl -s \
        -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.257/aws-java-sdk-bundle-1.12.257.jar \
        -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar \
        -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.3.6/postgresql-42.3.6.jar

WORKDIR /opt/pyetlapp

COPY parameters.py \
     batches_control.py \
     pyetlapp.py \
     data_manipulation.py \
     docker-entrypoint.sh ./

ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk \
    PATH=$PATH:$JAVA_HOME/bin \
    SPARK_HOME=/opt/spark \
    PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin \
    PYSPARK_PYTHON=/usr/bin/python3 \
    PYETLDB_HOST="" \
    PYETLDB_PORT="" \
    PYETLDB_DBNAME="" \
    PYETLDB_USER="" \
    PYETLDB_PASSWORD="" \
    DATA_SOURCE_USER="" \
    DATA_SOURCE_PASSWORD="" \
    AWS_ACCESS_KEY_ID="" \
    AWS_SECRET_ACCESS_KEY=""

ENTRYPOINT ["/opt/pyetlapp/docker-entrypoint.sh"]