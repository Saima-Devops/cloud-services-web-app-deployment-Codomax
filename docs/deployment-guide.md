# Cloud Services & Web App Deployment Manual

## 1. Project Overview

This project demonstrates deployment of a Flask web application using AWS cloud services.

### Architecture

```text
                         Internet
                            │
                            ▼
                     Elastic IP / EC2
                            │
                         Nginx :80
                            │
                            ▼
                  Gunicorn :127.0.0.1:5000
                            │
                            ▼
                       Flask App
                      /    |     \
                     /     |      \
                    ▼      ▼       ▼
                  RDS     S3    Secrets Manager
               PostgreSQL        DB credentials
                    │
                    ▼
               Private Subnets

        CloudWatch Agent
          │           │
          ▼           ▼
       Metrics       Logs
          │           │
          └──────┬────┘
                 ▼
             CloudWatch
                 │
                 ▼
          CloudWatch Alarm
                 │
                 ▼
                SNS
                 │
                 ▼
             Email Alert
```

---

## 2. AWS Services Used

| Service          | Purpose                                |
| ---------------- | -------------------------------------- |
| EC2              | Hosts the Flask application            |
| Elastic IP       | Provides a stable public IP            |
| VPC              | Provides isolated networking           |
| Subnets          | Separates public and private resources |
| Internet Gateway | Provides internet access to EC2        |
| Security Groups  | Controls network access                |
| RDS PostgreSQL   | Managed application database           |
| S3               | Private object storage                 |
| IAM              | Controls AWS permissions               |
| Secrets Manager  | Stores database credentials            |
| CloudWatch       | Monitoring and centralized logging     |
| CloudWatch Agent | Collects EC2 metrics and logs          |
| CloudWatch Alarm | Detects high CPU usage                 |
| SNS              | Sends alarm notifications              |
| Nginx            | Reverse proxy                          |
| Gunicorn         | Flask production server                |

---

## 3. Network Architecture

### VPC

```text
VPC: cloud-app-vpc
CIDR: 10.0.0.0/16
```

### Subnets

```text
Public Subnet
10.0.1.0/24
    │
    └── EC2 Web Server

Private Subnet
10.0.2.0/24
    │
    └── RDS

Private Subnet 2
10.0.3.0/24
    │
    └── RDS availability
```

The EC2 instance is placed in the public subnet.

RDS is private and is accessible only from the EC2 security group.

---

## 4. Security Groups

### Web Security Group

Allow:

```text
SSH 22   → My IP
HTTP 80  → 0.0.0.0/0
```

Port `5000` should **not** be publicly accessible.

Gunicorn listens only on:

```text
127.0.0.1:5000
```

### Database Security Group

Allow:

```text
PostgreSQL 5432
Source: Web Security Group
```

This allows the application server to communicate with RDS without exposing PostgreSQL publicly.

---

## 5. Application Deployment

### Install required software on EC2

Install:

```text
Python 3
pip
Git
PostgreSQL client
Nginx
CloudWatch Agent
AWS CLI
```

Create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r app/requirements.txt
```

---

## 6. Flask Application

The application provides:

```text
/
    Main application page

/health
    Application health check

/database-test
    Tests RDS connectivity

/resources
    Reads application resources from PostgreSQL

/storage-test
    Tests S3 connectivity
```

The application uses:

```text
Flask
Gunicorn
psycopg2
boto3
python-dotenv
```

---

## 7. RDS PostgreSQL

Create an RDS PostgreSQL instance using:

```text
Database: cloud_app
Username: cloud_user
Port: 5432
Public access: No
```

Place RDS in the private subnet group.

Create the database schema:

```sql
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Insert sample resources using the project's `seed.sql`.

---

## 8. S3 Storage

Create a private bucket:

```text
cloud-app-codomax2026
```

Keep:

```text
Block Public Access: ON
```

The application accesses S3 through the EC2 IAM role rather than storing AWS access keys.

---

## 9. IAM

Create an EC2 IAM role.

The role provides permissions for:

```text
S3 access
Secrets Manager access
CloudWatch Agent
```

Attach the required policies to the EC2 role.

Avoid putting AWS access keys inside the application or `.env` files.

---

## 10. Secrets Manager

Store the RDS credentials in AWS Secrets Manager.

Example secret name:

```text
cloud-app/rdscloud-app/rds
```

The Flask application retrieves the credentials through:

```text
boto3 → Secrets Manager → RDS credentials
```

The production server therefore does not require the database password in `.env`.

---

## 11. Gunicorn + Systemd

Create:

```text
/etc/systemd/system/cloud-app.service
```

The service should:

```text
User: ec2-user
WorkingDirectory: application directory
Bind: 127.0.0.1:5000
```

Enable it:

```bash
sudo systemctl enable cloud-app
sudo systemctl start cloud-app
```

Check:

```bash
sudo systemctl status cloud-app
```

---

## 12. Nginx

Create an Nginx reverse-proxy configuration.

Traffic flow:

```text
Internet
   ↓
Nginx :80
   ↓
Gunicorn 127.0.0.1:5000
   ↓
Flask
```

Enable Nginx:

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

Test:

```bash
curl http://127.0.0.1/health
```

---

## 13. CloudWatch Monitoring

Install the CloudWatch Agent and configure it to collect:

```text
CPU usage
Memory usage
Disk usage
System logs
Nginx access logs
Nginx error logs
```

Custom namespace:

```text
CloudApp/EC2
```

Log groups:

```text
/cloud-app/system
/cloud-app/nginx/access
/cloud-app/nginx/error
```

Start and enable the agent:

```bash
sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl start amazon-cloudwatch-agent
```

Verify:

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a status \
  -m ec2
```

---

## 14. CloudWatch Alarm

Create a CPU alarm:

```text
Metric: EC2 CPUUtilization
Statistic: Average
Period: 5 minutes
Condition: > 80%
```

Alarm name:

```text
cloud-app-ec2-high-cpu
```

Configure SNS to send an email notification when the alarm enters the `ALARM` state.

---

## 15. Elastic IP

Allocate an Elastic IP and associate it with the EC2 instance.

This prevents the public IP from changing after an EC2 stop/start operation.

Use the Elastic IP for:

```text
Browser access
SSH
Documentation
Screenshots
```

---

## 16. Final Verification

Test the application:

```text
http://ELASTIC_IP/
http://ELASTIC_IP/health
http://ELASTIC_IP/database-test
http://ELASTIC_IP/storage-test
```

Check services:

```bash
sudo systemctl is-active nginx
sudo systemctl is-active cloud-app
sudo systemctl is-active amazon-cloudwatch-agent
```

All should return:

```text
active
```

Verify AWS integrations:

```text
RDS → Database connection
S3 → Storage connection
Secrets Manager → Credentials retrieval
CloudWatch → Metrics and logs
SNS → Alarm notification
```

---

## 17. Re-implementation Checklist

To rebuild the project from scratch:

1. Create the Git repository and Flask application.
2. Create the AWS VPC and subnets.
3. Create route tables and Internet Gateway.
4. Create EC2 and its IAM role.
5. Create security groups.
6. Create the private RDS PostgreSQL instance.
7. Create the S3 bucket.
8. Create the Secrets Manager secret.
9. Deploy the Flask application to EC2.
10. Configure Gunicorn and systemd.
11. Configure Nginx.
12. Configure the CloudWatch Agent.
13. Create CloudWatch alarms and SNS notifications.
14. Allocate and associate an Elastic IP.
15. Test application, database, storage, monitoring, and logging.
16. Document the final architecture.

---

## 18. Security Rules

Never commit:

```text
.env
AWS access keys
database passwords
.pem files
private keys
credentials.json
```

Use:

```text
IAM roles
Secrets Manager
Private RDS
Private S3
Security Groups
Elastic IP
HTTPS/domain name when required
```

The production application should use IAM roles and Secrets Manager instead of hardcoded credentials.

---

## 19. Result

The completed system provides:

* A Flask web application running on EC2
* PostgreSQL database using RDS
* Private object storage using S3
* Secure credential storage using Secrets Manager
* IAM-based AWS access
* VPC and security-group isolation
* Nginx reverse proxy
* Gunicorn production server
* CloudWatch metrics and centralized logs
* CloudWatch CPU alerting
* SNS email notifications
* Stable EC2 public addressing through Elastic IP

This architecture can be reproduced by following the implementation order above and replacing project-specific names, IDs, endpoints, and credentials with values from the new AWS environment.
