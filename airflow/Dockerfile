FROM apache/airflow:2.10.5-python3.12

USER root

COPY airflow/requirements.txt /opt/airflow/requirements.txt
COPY packages/shared /opt/shared
COPY airflow/dags /opt/airflow/dags
COPY airflow/plugins /opt/airflow/plugins

RUN chown -R airflow:0 /opt/airflow/requirements.txt /opt/shared /opt/airflow/dags /opt/airflow/plugins

USER airflow

RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt \
    && pip install --no-cache-dir /opt/shared
