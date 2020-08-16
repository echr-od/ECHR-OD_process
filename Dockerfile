FROM python:3
MAINTAINER alexandre.quemy+echr@gmail.com

WORKDIR /tmp/echr_process/
COPY bin bin/
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir  -r requirements.txt
RUN python3 bin/download-nltk

ENTRYPOINT ["./entrypoint.sh"]