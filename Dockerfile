FROM python:3
MAINTAINER alexandre.quemy+echr@gmail.com

WORKDIR /tmp/echr_process/
COPY bin bin/
COPY requirements.txt .

RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install --no-cache-dir  -r requirements.txt
RUN python3.8 bin/download-nltk
RUN mv /root/nltk_data /usr/local/nltk_data

ENTRYPOINT ["./entrypoint.sh"]