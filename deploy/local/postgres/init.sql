DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'udp') THEN
      CREATE ROLE udp LOGIN PASSWORD 'udp';
   END IF;

   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
      CREATE ROLE airflow LOGIN PASSWORD 'airflow';
   END IF;
END
$$;

SELECT 'CREATE DATABASE udp OWNER udp'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'udp')
\gexec

SELECT 'CREATE DATABASE airflow OWNER airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')
\gexec
