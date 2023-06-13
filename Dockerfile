FROM python:3.10.11-bullseye

RUN apt update \
  && apt -y upgrade \
  && pip install --upgrade pip \
  && apt install -y --no-install-recommends build-essential git \
  && pip install fastapi \
  && pip install fuzzywuzzy \
  && pip install pysqlite3 \
  && pip install datetime \
  && pip install uvicorn \
  && apt autoremove -y \
  && apt clean all \
  && rm -rf /etc/apk/cache \
  && rm -rf /var/lib/apt/lists/* 
EXPOSE 8000
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
