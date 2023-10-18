FROM python:3.11

WORKDIR /lab02
COPY pipeline.py pipeline.py
COPY shelter1000.csv shelter1000.csv
COPY shelter_data.csv shelter_data.csv

RUN pip install pandas sqlalchemy psycopg2 numpy
# RUN python pipeline.py shelter_data.csv

ENTRYPOINT ["python", "pipeline.py" ]