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

## Recruiter quick verification (single sample CSV)

One sample file is included for practical verification:

- `testdata/crypto_price_history_10000_rich_with_errors.csv` (10,000 rows, 10 columns, with injected data-quality errors)

### 1. Start required services

```bash
docker compose up -d postgres redis api
docker compose --profile airflow up -d airflow-init airflow-scheduler
```

### 2. Upload sample dataset through API

```powershell
$sourceName = 'crypto-recruiter-sample-' + (Get-Date -Format 'yyyyMMddHHmmss')
$createBody = @{ name = $sourceName; source_type = 'crypto'; description = 'Recruiter sample import' } | ConvertTo-Json
$create = Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/v1/data-sources' -ContentType 'application/json' -Body $createBody
$sourceId = $create.id
curl.exe -X POST "http://localhost:8000/api/v1/data-sources/$sourceId/upload-csv" -F "file=@testdata/crypto_price_history_10000_rich_with_errors.csv;type=text/csv"
```

### 3. Validate raw rows in PostgreSQL

```sql
SELECT s.id, s.name, COUNT(r.id) AS raw_rows
FROM sources s
JOIN raw_data r ON r.source_id = s.id
WHERE s.name LIKE 'crypto-recruiter-sample-%'
GROUP BY s.id, s.name
ORDER BY s.name DESC
LIMIT 1;
```

### 4. Validate cleaned data and latest view

Materialize cleaned output from the uploaded source into `crypto_price_history_rich_cleaned`:

```powershell
$sourceId = (docker compose exec -T postgres psql -U postgres -d udp -t -A -c "SELECT s.id::text FROM sources s WHERE s.name LIKE 'crypto-recruiter-sample-%' ORDER BY s.created_at DESC LIMIT 1;").Trim()
$py = @"
from app.services.data_transformation_service import run_plugin_transformation_pipeline
from app.core.db import SessionLocal
from sqlalchemy import text
sid = '$sourceId'
cleaned, _ = run_plugin_transformation_pipeline(source_id=sid, source_type='crypto')
rows = cleaned.to_dict(orient='records')
with SessionLocal() as db:
	db.execute(text('CREATE TABLE IF NOT EXISTS crypto_price_history_rich_cleaned (id BIGSERIAL PRIMARY KEY, source_id UUID NOT NULL, symbol TEXT NOT NULL, asset_id TEXT NOT NULL, event_time TIMESTAMPTZ NOT NULL, price_usd NUMERIC NOT NULL, open_price_usd NUMERIC NOT NULL, min_price_usd_24h NUMERIC NOT NULL, max_price_usd_24h NUMERIC NOT NULL, volume_24h NUMERIC NOT NULL, market_cap_usd NUMERIC NOT NULL, change_pct_24h NUMERIC NOT NULL, loaded_at TIMESTAMPTZ NOT NULL DEFAULT now())'))
	db.execute(text('DELETE FROM crypto_price_history_rich_cleaned WHERE source_id = :sid'), {'sid': sid})
	payload = [{'sid': sid, 'symbol': r['symbol'], 'asset_id': r['asset_id'], 'event_time': r['event_time'].isoformat(), 'price_usd': float(r['price_usd']), 'open_price_usd': float(r['open_price_usd']), 'min_price_usd_24h': float(r['min_price_usd_24h']), 'max_price_usd_24h': float(r['max_price_usd_24h']), 'volume_24h': float(r['volume_24h']), 'market_cap_usd': float(r['market_cap_usd']), 'change_pct_24h': float(r['change_pct_24h'])} for r in rows]
	if payload:
		db.execute(text('INSERT INTO crypto_price_history_rich_cleaned (source_id, symbol, asset_id, event_time, price_usd, open_price_usd, min_price_usd_24h, max_price_usd_24h, volume_24h, market_cap_usd, change_pct_24h) VALUES (:sid, :symbol, :asset_id, CAST(:event_time AS timestamptz), :price_usd, :open_price_usd, :min_price_usd_24h, :max_price_usd_24h, :volume_24h, :market_cap_usd, :change_pct_24h)'), payload)
	db.commit()
print(f'INSERTED_CLEANED_ROWS={len(rows)}')
"@
docker compose exec -T api python -c $py
```

`crypto_price_history_rich_cleaned_latest` keeps the latest row per `(source_id, symbol)`.

```sql
CREATE OR REPLACE VIEW public.crypto_price_history_rich_cleaned_latest AS
SELECT DISTINCT ON (source_id, symbol)
	id,
	source_id,
	symbol,
	asset_id,
	event_time,
	price_usd,
	open_price_usd,
	min_price_usd_24h,
	max_price_usd_24h,
	volume_24h,
	market_cap_usd,
	change_pct_24h,
	loaded_at
FROM public.crypto_price_history_rich_cleaned
ORDER BY source_id, symbol, event_time DESC, id DESC;
```

```sql
SELECT source_id, COUNT(*) AS latest_rows
FROM public.crypto_price_history_rich_cleaned_latest
GROUP BY source_id
ORDER BY source_id;
```

### 5. Scheduler verification (10-second backoff DAG)

```bash
docker compose exec airflow-scheduler airflow dags unpause crypto_market_ingest_10s_backoff
docker compose exec airflow-scheduler airflow dags test crypto_market_ingest_10s_backoff 2026-03-14
```

```sql
SELECT s.name, COUNT(*) AS raw_rows
FROM raw_data r
JOIN sources s ON s.id = r.source_id
WHERE s.name = 'crypto-coingecko-10s-backoff'
GROUP BY s.name;
```

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
