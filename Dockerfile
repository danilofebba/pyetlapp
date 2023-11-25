FROM alpine:latest AS tg-spark-base
RUN apk update \
    && apk --no-cache add \
        bash \
        coreutils \
        procps \
        curl \
        openjdk11 \
        python3
#RUN curl -s https://dlcdn.apache.org/spark/spark-3.4.1/spark-3.4.1-bin-hadoop3-scala2.13.tgz -o /tmp/spark-3.4.1-bin-hadoop3-scala2.13.tgz \
#    && tar -zxvf /tmp/spark-3.4.1-bin-hadoop3-scala2.13.tgz -C /opt \
#    && mv /opt/spark-3.4.1-bin-hadoop3-scala2.13 /opt/spark \
#    && rm /tmp/spark-3.4.1-bin-hadoop3-scala2.13.tgz
################################# TMP #################################################
COPY jars/spark-3.4.1-bin-hadoop3-scala2.13.tgz /tmp
RUN tar -zxvf /tmp/spark-3.4.1-bin-hadoop3-scala2.13.tgz -C /opt \
    && mv /opt/spark-3.4.1-bin-hadoop3-scala2.13 /opt/spark \
    && rm /tmp/spark-3.4.1-bin-hadoop3-scala2.13.tgz
#######################################################################################
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk \
    SPARK_HOME=/opt/spark \
    PATH=$PATH:/usr/lib/jvm/java-11-openjdk/bin:/opt/spark/bin:/opt/spark/sbin

FROM tg-spark-base AS tg-spark-master
ENV INSTANCE=MASTER
WORKDIR /opt/spark
COPY docker-entrypoint.sh ./
ENTRYPOINT ["/opt/spark/docker-entrypoint.sh"]

FROM tg-spark-base AS tg-spark-worker
ENV INSTANCE=WORKER
WORKDIR /opt/spark
COPY docker-entrypoint.sh ./
ENTRYPOINT ["/opt/spark/docker-entrypoint.sh"]

FROM tg-spark-base AS tg-pyetlapp
RUN apk --no-cache add \
    python3-dev \
    py3-pip \
    py3-boto3 \
    awc-cli
############################# TMP ####################################
RUN apk --no-cache add jupyter-notebook 
######################################################################
RUN python3 -m pip install --upgrade --no-cache-dir pip \
    setuptools \
    wheel \
    python-dateutil \
    findspark \
    psycopg[binary,pool]
#RUN cd /opt/spark/jars \
#    && curl -s \
#        -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.505/aws-java-sdk-bundle-1.12.505.jar \
#        -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
#        -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar \
#        -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar
############################# TMP ####################################
COPY jars/*.jar /opt/spark/jars
######################################################################
WORKDIR /opt/pyetlapp
COPY src \
     docker-entrypoint.sh ./
ENV PYSPARK_PYTHON=/usr/bin/python3
ENTRYPOINT ["/opt/pyetlapp/docker-entrypoint.sh"]
