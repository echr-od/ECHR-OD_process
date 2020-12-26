FROM python:3.8

WORKDIR /tmp/echr_process/
COPY bin bin/
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip==20.3.3
RUN python3 -m pip install --no-cache-dir  -r requirements.txt
RUN python3 bin/download-nltk
RUN mv /root/nltk_data /usr/local/nltk_data

ENTRYPOINT ["./entrypoint.sh"]