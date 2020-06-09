FROM python:3.8-alpine3.11

LABEL maintainer = "Michele Salanti, Ivan Donati"

COPY ./feedgram /app/
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

VOLUME /app/config.ini
VOLUME /app/socialFeedgram.sqlite3

CMD ["./app_handler.py"]
