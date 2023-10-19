# pyetlapp
Python ETL Application

## Local
- Edit /etc/hosts
- Read jars/README.md

## AWS
### Starting
[AWS > IAM > Getting Started > Create Administrators Group](https://docs.aws.amazon.com/pt_br/IAM/latest/UserGuide/getting-started_create-admin-group.html)
### Create bucket
#### Step 0
```bash
aws s3api create-bucket \
    --bucket my-bucket \
    --region us-east-1 \
    --object-ownership BucketOwnerEnforced

aws s3api put-public-access-block \
    --bucket my-bucket \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws s3api put-bucket-tagging \
    --bucket my-bucket \
    --tagging 'TagSet=[{Key=project,Value=01}]'

aws s3api put-object \
    --bucket my-bucket \
    --key my-data-lake/
```
### Create database
#### Step 1
Minimum requirements:
```bash
aws rds create-db-instance \
    --db-instance-identifier "my-db-instance" \
    --engine postgres \
    --engine-version 13.6 \
    --db-instance-class db.t3.micro \
    --storage-type gp2 \
    --allocated-storage 20 \
    --max-allocated-storage 21 \
    --storage-encrypted \
    --port 5432 \
    --db-name pyetldb \
    --master-username "my_user" \
    --master-user-password "my_password" \
    --publicly-accessible \
    --no-multi-az \
    --backup-retention-period 1 \
    --tags Key="my_key",Value="my_value"
```
### Launch instance EC2
#### Step 2
Minimum requirements:
```bash
aws ec2 run-instances \
    --image-id ami-052efd3df9dad4825 \
    --instance-type t3.small \
    --subnet-id "my-subnet-id" \
    --security-group-ids "my-security-group-id" \
    --associate-public-ip-address \
    --key-name "my_key_pair"
```
#### Step 3
```bash
sudo apt update
sudo apt install htop
sudo apt install vim
sudo apt install git
sudo apt install openjdk-8-jdk
sudo apt install python3-pip
sudo apt install awscli

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools
python3 -m pip install --upgrade wheel
python3 -m pip install --upgrade python-dateutil
python3 -m pip install --upgrade findspark
python3 -m pip install --upgrade psycopg2-binary

curl -s https://archive.apache.org/dist/spark/spark-3.1.3/spark-3.1.3-bin-hadoop3.2.tgz -o /tmp/spark-3.1.3-bin-hadoop3.2.tgz
sudo tar -zxvf /tmp/spark-3.1.3-bin-hadoop3.2.tgz -C /opt
sudo mv /opt/spark-3.1.3-bin-hadoop3.2 /opt/spark
sudo rm /tmp/spark-3.1.3-bin-hadoop3.2.tgz

sudo git clone https://github.com/danilofebba/pyetlapp.git /opt/pyetlapp
sudo mkdir -p /opt/pyetlapp/jars
sudo curl -s https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.257/aws-java-sdk-bundle-1.12.257.jar -o /opt/pyetlapp/jars
sudo curl -s https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar -o /opt/pyetlapp/jars
sudo curl -s https://repo1.maven.org/maven2/org/postgresql/postgresql/42.3.6/postgresql-42.3.6.jar -o /opt/pyetlapp/jars

echo "export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64" >> ~/.bashrc
echo "export PATH=$PATH:$JAVA_HOME/bin" >> ~/.bashrc
echo "export SPARK_HOME=/opt/spark" >> ~/.bashrc
echo "export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin" >> ~/.bashrc
echo "export PYSPARK_PYTHON=/usr/bin/python3" >> ~/.bashrc

echo "export PYETLDB_HOST=\"my-endpoint\"" >> ~/.bashrc
echo "export PYETLDB_PORT=\"my_port\"" >> ~/.bashrc
echo "export PYETLDB_DBNAME=\"pyetldb\"" >> ~/.bashrc
echo "export PYETLDB_USER=\"my_user\"" >> ~/.bashrc
echo "export PYETLDB_PASSWORD=\"my_password\"" >> ~/.bashrc

echo "export DATA_SOURCE_USER=\"my_user\"" >> ~/.bashrc
echo "export DATA_SOURCE_PASSWORD=\"my_password\"" >> ~/.bashrc

source ~/.bashrc
```
#### Step 4
Configure your security credentials on the EC2 instance. Link for reference: [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
#### Step 5
Configure your application parameters file: /opt/pyetlapp/parameters.py
#### Step 6
Configure crontab

```bash
crontab -l > my_crontab
echo "0 4 * * * /usr/bin/python3 /opt/pyetlapp/pyetlapp.py" >> my_crontab
crontab my_crontab
rm my_crontab
```

ideias
Dependência de ordens

Coluna com prioridade da ordem de execução e dependência da execuçào
tras primeiro os sem dependencia
tras depois os com dependências onde o numero de pacotes pai é igual a zero

sempre ordenados por ordem de execução

[Hadoop-AWS module: Integration with Amazon Web Services](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html)



serviço A: cadastro de objetos no banco de dados. O serviço em python que lê o json de parametros e cadastra no banco

ele cadstra novos
gera json apartir do registro


serviço B: dispar Job para o master

seriço C: paralelismo de disparaos de pacotes atraves de consulta de batches com inclusão de novos batches a partir das configurações ja cadastradas no banco
