# AWS RDS PostgreSQL

## Database

Identifier:

`cloud-app-postgres`

Engine:

PostgreSQL

Database:

`cloud_app`

Application user:

`cloud_user`

Port:

`5432`

## Network

VPC:

`cloud-app-vpc`

DB subnet group:

`cloud-app-db-subnet-group`

Private subnets:

- `10.0.2.0/24`
- `10.0.3.0/24`

Public access:

`No`

## Security

Security group:

`cloud-app-db-sg`

Inbound PostgreSQL access:

```text
EC2 web security group
        |
        | TCP 5432
        v
RDS PostgreSQL
```
