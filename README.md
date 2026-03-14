# Universal Data Platform

Monorepo scaffold for a data platform built with FastAPI, Pandas, Apache Airflow, PostgreSQL, and Docker for local-first development.

## Project layout

- `apps/api` - FastAPI service exposing operational and domain APIs.
- `airflow` - DAGs, plugins, and image definition for orchestration workloads.
- `packages/shared` - reusable Python utilities shared by API and Airflow.
- `.github/workflows` - CI workflow for GitHub Actions.

## Local development

1. Create a local `.env` file from `.env.example`.
2. Start the core local stack with `docker compose up --build`.
3. API will be available on `http://localhost:8000`.
4. Start Airflow only when needed with `docker compose --profile airflow up --build`.
5. Airflow webserver will be available on `http://localhost:8080`.

## Local data workflows

- CSV archives can be loaded into PostgreSQL and explored through pgAdmin.
- Airflow can fetch live crypto prices from CoinGecko with the `crypto_market_ingest_pipeline` DAG.
- Raw records are stored in PostgreSQL and can be queried either from tables or prepared SQL views.

## pgAdmin quick start

Use these connection settings in pgAdmin:

- Host: `localhost`
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Maintenance database: `postgres`

Useful relations after local imports:

- `public.crypto_csv_history` - full historical table imported from CSV archive files.
- `public.crypto_csv_latest` - latest row per symbol from the imported archive.
- `public.crypto_latest` - latest live snapshot fetched by the Airflow DAG.

Useful API endpoints:

- `GET /api/v1/crypto/archive/latest` - latest archive row per symbol.
- `GET /api/v1/crypto/live/latest` - latest live row per symbol from Airflow ingestion.
- Both endpoints support `limit` and optional `symbol` query parameters.

Example query:

```sql
SELECT symbol, event_time, close, marketcap
FROM public.crypto_csv_latest
ORDER BY symbol;
```

## What is included

- A working FastAPI app with a health endpoint.
- A sample Airflow DAG that uses Pandas.
- A scheduled Airflow DAG that fetches live crypto prices from CoinGecko.
- A reusable shared package installed into both runtime images.
- Dockerfiles for the API and Airflow.
- GitHub Actions workflow for CI.
