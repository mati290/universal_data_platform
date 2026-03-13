# Terraform for Azure

This directory provisions the baseline Azure infrastructure for the platform:

- Resource group
- Virtual network and subnets
- Azure Container Registry
- Azure Kubernetes Service
- Azure Database for PostgreSQL Flexible Server

## Suggested workflow

1. Copy `terraform.tfvars.example` to `terraform.tfvars` and adjust values.
2. Run `terraform init`.
3. Run `terraform fmt -recursive`.
4. Run `terraform validate`.
5. Run `terraform plan`.
6. Apply after review.
