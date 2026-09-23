# Application Architecture

```text
                    Internet
                       |
                       v
                Public IP / DNS
                       |
                       v
                    Nginx
                       |
                       v
              Cloud Compute VM
                       |
              +--------+--------+
              |                 |
              v                 v
       Managed Database   Object Storage
              |
              v
       Cloud Monitoring
<EOF>
