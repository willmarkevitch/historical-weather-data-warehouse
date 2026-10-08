FROM apache/airflow:3.3.2-python3.14

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir \
    "apache-airflow[postgres]==3.3.2" \
    -r /requirements.txt \
    "pytest==9.1.1"
