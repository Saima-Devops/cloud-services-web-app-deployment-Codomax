# Security

## Security Principles

- Use least-privilege IAM policies.
- Never commit credentials to Git.
- Keep database resources private where possible.
- Expose only required network ports.
- Store secrets using a cloud secrets-management service.
- Use HTTPS in production.
- Monitor application and infrastructure logs.

# IAM Security

## EC2 IAM Role

The application EC2 instance uses an IAM role instead of storing long-lived AWS access keys on the server.

Role:

```text
cloud-app-ec2-role
```

## S3 Policy

The role uses the policy:

`CloudAppS3AccessPolicy`

The policy grants the application only the S3 permissions required for its application bucket.

- Allowed operations
- s3:ListBucket
- s3:GetObject
- s3:PutObject
- s3:DeleteObject