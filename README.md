# pyetlapp
Python ETL Application

## AWS
### Create database
Minimum requirements:
```bash
aws rds create-db-instance \
    --db-instance-identifier my-db-instance \
    --engine postgres \
    --engine-version "13.6" \
    --db-instance-class db.t3.micro \
    --storage-type gp2 \
    --allocated-storage 20 \
    --max-allocated-storage 21 \
    --storage-encrypted \
    --port 5432 \
    --db-name pyetldb \
    --master-username my_user \
    --master-user-password my_password \
    --publicly-accessible \
    --no-multi-az \
    --backup-retention-period 1 \
    --tags Key="my_project_name",Value="my_project_code"
```
### Launch instance EC2
Minimum requirements:
```bash
aws ec2 run-instances \
    --image-id ami-052efd3df9dad4825 \
    --instance-type t3.small \
    --subnet-id **my-subnet-id** \
    --security-group-ids my-security-group-id \
    --associate-public-ip-address \
    --key-name my_key_pair
```
