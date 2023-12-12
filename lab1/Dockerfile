FROM python:3.11

WORKDIR /lab01
COPY pipeline.py pipeline_c.py
COPY stem_jobs_nyc_dataset.csv stem_jobs_nyc_dataset.csv
RUN pip install pandas
RUN python pipeline_c.py stem_jobs_nyc_dataset.csv stem_jobs_output.csv

ENTRYPOINT [ "bash" ]