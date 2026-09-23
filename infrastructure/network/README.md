# AWS Network Infrastructure

## VPC

Name:

`cloud-app-vpc`

CIDR:

`10.0.0.0/16`

## Subnets

### Public Subnet

Name:

`cloud-app-public-subnet`

CIDR:

`10.0.1.0/24`

Purpose:

- EC2 web server
- Internet-facing application

### Private Subnet

Name:

`cloud-app-private-subnet`

CIDR:

`10.0.2.0/24`

Purpose:

- RDS PostgreSQL
- Private database connectivity

## Internet Gateway

Name:

`cloud-app-igw`

The Internet Gateway provides Internet connectivity for resources in the public subnet when the subnet route table contains a route to the gateway.

## Route Table

Name:

`cloud-app-public-rt`

Route:

```
0.0.0.0/0 → Internet Gateway
```

## Associated subnet:

`cloud-app-public-subnet`


## Security Groups

### Web Security Group

Name:

`cloud-app-web-sg`

Inbound:

- SSH 22 from My IP
- HTTP 80 from the Internet
- TCP 5000 from My IP during development/testing
- Database Security Group

Name:

`cloud-app-db-sg`

Inbound:

- PostgreSQL 5432 from cloud-app-web-sg

PostgreSQL is not exposed directly to the public Internet.