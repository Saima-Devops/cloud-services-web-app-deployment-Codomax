
### `infrastructure/network/network-diagram.md`



# Network Architecture

```text
                         Internet
                            |
                            v
                  +-------------------+
                  | Internet Gateway  |
                  +-------------------+
                            |
                            v
              +---------------------------+
              |       cloud-app-vpc        |
              |        10.0.0.0/16         |
              |                           |
              |  +---------------------+  |
              |  |   Public Subnet     |  |
              |  |   10.0.1.0/24       |  |
              |  |                     |  |
              |  |       EC2           |  |
              |  |   Web Application   |  |
              |  +----------+----------+  |
              |             |             |
              |             | TCP 5432    |
              |             v             |
              |  +---------------------+  |
              |  |   Private Subnet    |  |
              |  |   10.0.2.0/24       |  |
              |  |                     |  |
              |  |       RDS           |  |
              |  |    PostgreSQL       |  |
              |  +---------------------+  |
              +---------------------------+

              Security Groups:
              EC2 → cloud-app-web-sg
              RDS → cloud-app-db-sg
```