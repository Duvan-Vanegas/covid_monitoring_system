FROM apache/airflow:2.7.2

USER root

# Bogotá (UTC-5)
ENV TZ=America/Bogota
RUN apt-get update && \
    apt-get install -y sqlite3 tzdata && \
    ln -fs /usr/share/zoneinfo/America/Bogota /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

COPY requirements.txt .

USER airflow
RUN pip install --no-cache-dir -r requirements.txt

USER root
COPY dags/ /opt/airflow/dags/
COPY data_processing/ /opt/airflow/data_processing/
COPY data/ /opt/airflow/data/

USER airflow
