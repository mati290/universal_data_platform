# Universal Data Platform

Monorepo scaffold for a data platform built with FastAPI, Pandas, Apache Airflow, PostgreSQL, Docker, Kubernetes, Terraform, and Azure.

## Project layout

- `apps/api` - FastAPI service exposing operational and domain APIs.
- `airflow` - DAGs, plugins, and image definition for orchestration workloads.
- `packages/shared` - reusable Python utilities shared by API and Airflow.
- `deploy/kubernetes` - Kustomize manifests for the API and Helm values for Airflow.
- `infra/terraform` - Azure infrastructure modules for networking, ACR, AKS, and PostgreSQL.
- `.github/workflows` - CI and CD pipelines for GitHub Actions.

## Local development

1. Create a local `.env` file from `.env.example`.
2. Start the local stack with `docker compose up --build`.
3. API will be available on `http://localhost:8000`.
4. Airflow webserver will be available on `http://localhost:8080`.

## What is included

- A working FastAPI app with a health endpoint.
- A sample Airflow DAG that uses Pandas.
- A reusable shared package installed into both runtime images.
- Dockerfiles for the API and Airflow.
- Kubernetes base manifests and a dev overlay.
- Terraform modules for Azure resource group, network, ACR, AKS, and PostgreSQL Flexible Server.
- GitHub Actions workflows for CI and deployment.

## Azure deployment flow

1. Adjust `infra/terraform/terraform.tfvars` based on `terraform.tfvars.example`.
2. Run `terraform init`, `terraform validate`, and `terraform plan` from `infra/terraform`.
3. Apply infrastructure after review.
4. Configure GitHub repository secrets and variables used by `.github/workflows/cd.yml`.
5. Build and push container images to Azure Container Registry.
6. Deploy the API with Kustomize and Airflow with Helm values.
