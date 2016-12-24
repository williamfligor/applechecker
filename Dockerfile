FROM ubuntu:14.04

COPY stock.py .
RUN apt-get update && apt-get install -y \
    python \
    python-pip \
 && pip install -r requirements.txt \
 && rm -rf /var/lib/apt/lists/*

CMD python -u stock.py $MODEL $ZIP $SEC
