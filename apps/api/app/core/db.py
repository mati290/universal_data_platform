from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def _migrate_raw_data_table() -> None:
	with engine.begin() as connection:
		inspector = inspect(connection)
		if not inspector.has_table("raw_data"):
			return

		columns = {column["name"] for column in inspector.get_columns("raw_data")}

		if "source_id" not in columns:
			connection.execute(text("ALTER TABLE raw_data ADD COLUMN source_id UUID"))

		if "raw_json" not in columns:
			connection.execute(text("ALTER TABLE raw_data ADD COLUMN raw_json JSONB"))

		if "created_at" not in columns:
			connection.execute(text("ALTER TABLE raw_data ADD COLUMN created_at TIMESTAMPTZ DEFAULT now()"))

		if "dataset_id" in columns:
			connection.execute(
				text(
					"""
					UPDATE raw_data AS rd
					SET source_id = d.source_id
					FROM datasets AS d
					WHERE rd.dataset_id = d.id AND rd.source_id IS NULL
					"""
				)
			)
			connection.execute(text("ALTER TABLE raw_data ALTER COLUMN dataset_id DROP NOT NULL"))
			connection.execute(text("ALTER TABLE raw_data DROP CONSTRAINT IF EXISTS raw_data_dataset_id_fkey"))
			connection.execute(text("ALTER TABLE raw_data DROP COLUMN IF EXISTS dataset_id"))

		if "payload" in columns:
			connection.execute(text("UPDATE raw_data SET raw_json = payload WHERE raw_json IS NULL"))
			connection.execute(text("ALTER TABLE raw_data DROP COLUMN IF EXISTS payload"))

		if "ingested_at" in columns:
			connection.execute(text("UPDATE raw_data SET created_at = ingested_at WHERE created_at IS NULL"))
			connection.execute(text("ALTER TABLE raw_data DROP COLUMN IF EXISTS ingested_at"))

		connection.execute(text("UPDATE raw_data SET raw_json = '{}'::jsonb WHERE raw_json IS NULL"))
		connection.execute(text("UPDATE raw_data SET created_at = now() WHERE created_at IS NULL"))
		connection.execute(text("DELETE FROM raw_data WHERE source_id IS NULL"))

		connection.execute(text("ALTER TABLE raw_data ALTER COLUMN source_id SET NOT NULL"))
		connection.execute(text("ALTER TABLE raw_data ALTER COLUMN raw_json SET NOT NULL"))
		connection.execute(text("ALTER TABLE raw_data ALTER COLUMN created_at SET NOT NULL"))

		connection.execute(text("CREATE INDEX IF NOT EXISTS ix_raw_data_source_id ON raw_data(source_id)"))
		connection.execute(
			text(
				"""
				DO $$
				BEGIN
					IF NOT EXISTS (
						SELECT 1
						FROM pg_constraint
						WHERE conname = 'raw_data_source_id_fkey'
					) THEN
						ALTER TABLE raw_data
						ADD CONSTRAINT raw_data_source_id_fkey
						FOREIGN KEY (source_id)
						REFERENCES sources(id)
						ON DELETE CASCADE;
					END IF;
				END
				$$;
				"""
			)
		)


def _ensure_crypto_tables_and_views() -> None:
	def _execute_ddl_safely(sql: str) -> None:
		with engine.begin() as connection:
			try:
				connection.execute(text(sql))
			except ProgrammingError as exc:
				message = str(exc).lower()
				if "must be owner" in message or "permission denied" in message:
					return
				raise

	_execute_ddl_safely(
			"""
			CREATE TABLE IF NOT EXISTS crypto_csv_history (
				id BIGSERIAL PRIMARY KEY,
				source_file TEXT NOT NULL,
				s_no INTEGER NOT NULL,
				coin_name TEXT NOT NULL,
				symbol TEXT NOT NULL,
				event_time TIMESTAMPTZ NOT NULL,
				high NUMERIC NOT NULL,
				low NUMERIC NOT NULL,
				open NUMERIC NOT NULL,
				close NUMERIC NOT NULL,
				volume NUMERIC NOT NULL,
				marketcap NUMERIC NOT NULL,
				created_at TIMESTAMPTZ NOT NULL DEFAULT now()
			)
			"""
		)
	_execute_ddl_safely(
			"""
			CREATE INDEX IF NOT EXISTS ix_crypto_csv_history_symbol_time
			ON crypto_csv_history(symbol, event_time DESC)
			"""
		)
	_execute_ddl_safely(
			"""
			CREATE OR REPLACE VIEW crypto_csv_latest AS
			SELECT DISTINCT ON (symbol)
				id,
				source_file,
				coin_name,
				symbol,
				event_time,
				high,
				low,
				open,
				close,
				volume,
				marketcap,
				created_at
			FROM crypto_csv_history
			ORDER BY symbol, event_time DESC, id DESC
			"""
		)
	_execute_ddl_safely(
			"""
			CREATE OR REPLACE VIEW crypto_latest AS
			SELECT DISTINCT ON ((r.raw_json->>'symbol'))
				r.id,
				s.name AS source_name,
				r.created_at,
				r.raw_json->>'symbol' AS symbol,
				r.raw_json->>'asset_id' AS asset_id,
				(r.raw_json->>'price_usd')::numeric AS price_usd,
				(r.raw_json->>'event_time')::timestamptz AS event_time,
				r.raw_json->>'provider' AS provider
			FROM raw_data AS r
			JOIN sources AS s ON s.id = r.source_id
			WHERE s.name = 'crypto-coingecko'
			  AND r.raw_json ? 'symbol'
			  AND r.raw_json ? 'price_usd'
			ORDER BY (r.raw_json->>'symbol'), COALESCE((r.raw_json->>'event_time')::timestamptz, r.created_at) DESC, r.id DESC
			"""
		)


def init_db() -> None:
	import app.models.tables  # noqa: F401

	Base.metadata.create_all(bind=engine)
	_migrate_raw_data_table()
	_ensure_crypto_tables_and_views()
