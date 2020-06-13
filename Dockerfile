FROM python:3.8-alpine3.11

LABEL maintainer = "Michele Salanti, Ivan Donati"

COPY . /app/

WORKDIR /app

RUN pip3 install . && rm -rf ./*

VOLUME /app/config.ini
VOLUME /app/socialFeedgram.sqlite3

CMD ["feedgram"]
