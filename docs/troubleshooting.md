# Troubleshooting Guide

This guide covers common problems when deploying and operating the Cloud Services & Web App Deployment project.

## 1. Flask Import Error

### Error

```text
ModuleNotFoundError: No module named 'storage'
```

### Cause

The module is inside the `app` package but was imported as a top-level module.

### Fix

Use:

```python
from app.storage import list_bucket_objects
```

Instead of:

```python
from storage import list_bucket_objects
```

Run the application from the project root.

---

## 2. Gunicorn Service Not Running

Check:

```bash
sudo systemctl status cloud-app
```

View logs:

```bash
sudo journalctl -u cloud-app -n 50 --no-pager
```

Restart:

```bash
sudo systemctl restart cloud-app
```

Check that Gunicorn is listening:

```bash
sudo ss -lntp | grep 5000
```

Gunicorn should listen on:

```text
127.0.0.1:5000
```

---

## 3. Nginx Returns 502 Bad Gateway

Check both services:

```bash
sudo systemctl status nginx
sudo systemctl status cloud-app
```

Test Gunicorn directly:

```bash
curl http://127.0.0.1:5000/health
```

If this fails, troubleshoot the Flask/Gunicorn service first.

Check Nginx errors:

```bash
sudo tail -50 /var/log/nginx/error.log
```

---

## 4. RDS Connection Failure

Test DNS resolution:

```bash
getent hosts cloud-app-postgres.c0bwy2eiemx4.us-east-1.rds.amazonaws.com
```

Test PostgreSQL connectivity:

```bash
nc -zv cloud-app-postgres.c0bwy2eiemx4.us-east-1.rds.amazonaws.com 5432
```

Check:

* RDS is available.
* RDS is in the private subnet.
* Database security group allows TCP `5432` from the EC2 security group.
* Database name and username are correct.
* Secrets Manager contains the correct credentials.
* PostgreSQL SSL is enabled by the application.

The application uses:

```python
sslmode="require"
```

---

## 5. Secrets Manager Access Failure

Test IAM access without displaying the secret:

```bash
aws secretsmanager get-secret-value \
  --secret-id "cloud-app/rdscloud-app/rds" \
  --query 'SecretString' \
  --output text > /dev/null && echo "Secrets Manager access: OK"
```

If access is denied, check that the EC2 IAM role has permission for:

```text
secretsmanager:GetSecretValue
```

Also verify that the policy resource matches the actual secret ARN.

Never put the secret value into Git or documentation.

---

## 6. S3 Access Failure

Check the EC2 identity:

```bash
aws sts get-caller-identity
```

Test the bucket:

```bash
aws s3 ls s3://cloud-app-codomax2026
```

Check:

* EC2 IAM role has S3 permissions.
* Bucket name is correct.
* AWS region is correct.
* S3 Block Public Access remains enabled.

The application should use the IAM role rather than hardcoded AWS credentials.

---

## 7. CloudWatch Agent Shows `stopped`

Check:

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a status \
  -m ec2
```

If the configuration is missing, verify:

```bash
sudo ls -l /opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-agent.json
```

Apply the configuration:

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-agent.json \
  -s
```

Then check:

```bash
sudo systemctl status amazon-cloudwatch-agent --no-pager
```

---

## 8. CloudWatch Logs Are Not Appearing

Check the agent log:

```bash
sudo tail -100 \
/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

Verify the IAM role has CloudWatch permissions.

In AWS Console, check:

**CloudWatch → Logs → Log groups**

Expected groups:

```text
/cloud-app/system
/cloud-app/nginx/access
/cloud-app/nginx/error
```

Make sure the AWS Console is set to the same region as the EC2 instance.

---

## 9. EC2 Public IP Changed

A normal EC2 public IPv4 address can change after a stop/start operation.

Solution:

**EC2 → Elastic IPs → Allocate → Associate with the instance**

Use the Elastic IP for future:

* Browser access
* SSH
* Documentation
* Screenshots

---

## 10. SSH Connection Failure

From Windows PowerShell:

```powershell
ssh -i .\cloud-app-key.pem ec2-user@ELASTIC_IP
```

Check:

* The Elastic IP is correct.
* The EC2 instance is running.
* Security group allows SSH `22` from your current public IP.
* The `.pem` file is the correct key pair.
* The username is `ec2-user` for Amazon Linux.

---

## 11. HTTP Connection Failure

Check:

```bash
sudo systemctl status nginx
```

Verify port 80:

```bash
sudo ss -lntp | grep :80
```

Check the EC2 security group allows:

```text
HTTP 80 → 0.0.0.0/0
```

Then test:

```text
http://ELASTIC_IP
```

---

## 12. Database Authentication Failure

If PostgreSQL reports authentication errors:

1. Verify the username.
2. Verify the database name.
3. Verify the password stored in Secrets Manager.
4. Confirm the application is using the correct secret name.
5. Restart Gunicorn after configuration changes.

```bash
sudo systemctl restart cloud-app
```

Never paste database passwords into terminal history, Git, documentation, or screenshots.

---

## 13. Service Restart After Reboot

Check:

```bash
sudo systemctl is-enabled nginx
sudo systemctl is-enabled cloud-app
sudo systemctl is-enabled amazon-cloudwatch-agent
```

Expected:

```text
enabled
```

If necessary:

```bash
sudo systemctl enable nginx
sudo systemctl enable cloud-app
sudo systemctl enable amazon-cloudwatch-agent
```

---

## 14. Useful Diagnostic Commands

### Application logs

```bash
sudo journalctl -u cloud-app -n 100 --no-pager
```

### Nginx error log

```bash
sudo tail -100 /var/log/nginx/error.log
```

### Nginx access log

```bash
sudo tail -100 /var/log/nginx/access.log
```

### CloudWatch Agent log

```bash
sudo tail -100 \
/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

### Listening ports

```bash
sudo ss -lntp
```

### Running services

```bash
sudo systemctl --type=service --state=running
```

---

## 15. Security Reminder

When troubleshooting, never expose or commit:

```text
.env
database passwords
AWS access keys
Secrets Manager values
.pem files
private keys
```

Use IAM roles and Secrets Manager for credentials and keep production secrets outside the Git repository.
