# Kubernetes deployment layout

- `base` contains reusable Kustomize manifests for the FastAPI service.
- `overlays/dev` contains development-specific patches.
- `airflow/values-dev.yaml` contains Helm values for the Apache Airflow chart.

## API deployment

Apply the API manifests with:

`kubectl apply -k deploy/kubernetes/overlays/dev`

## Airflow deployment

Use the official Apache Airflow Helm chart and pass `deploy/kubernetes/airflow/values-dev.yaml` as the values file.
