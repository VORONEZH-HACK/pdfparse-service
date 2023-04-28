FROM python:3.11-bullseye

ARG WORK_DIR=/opt/mnt
ENV PYTHONPATH=$WORK_DIR

WORKDIR $WORK_DIR

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && python -m spacy download en_core_web_sm && python -m nltk.downloader words && python -m nltk.downloader stopwords

COPY ./app ./app

EXPOSE 8080
CMD ["python", "-m", "app"]
