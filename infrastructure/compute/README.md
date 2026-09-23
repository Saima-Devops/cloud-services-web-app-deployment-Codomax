# AWS EC2 Compute

## Instance

Name:

`cloud-app-web-server`

Purpose:

Run the Flask web application.

## Operating System

Amazon Linux 2023

## Network

VPC:

`cloud-app-vpc`

Subnet:

`cloud-app-public-subnet`

Subnet CIDR:

`10.0.1.0/24`

## Security Group

`cloud-app-web-sg`

Allowed development traffic:

- SSH: TCP 22 from administrator IP
- HTTP: TCP 80 from the Internet
- Flask development port: TCP 5000 from administrator IP

Port `5000` is temporary for development/testing.

Production traffic will use:

```text
Internet
    ↓
Nginx
    ↓
Gunicorn
    ↓
Flask
```

The EC2 instance will eventually run:

- Python
- Flask
- Gunicorn
- Nginx
- PostgreSQL client tools
- Git