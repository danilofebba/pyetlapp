### Create database
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
    --db-name my_database \
    --master-username "my_user" \
    --master-user-password "my_password" \
    --publicly-accessible \
    --no-multi-az \
    --backup-retention-period 1 \
    --tags Key="my_key",Value="my_value"
```
