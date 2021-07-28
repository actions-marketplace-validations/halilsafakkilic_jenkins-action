FROM python:3.9.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY src .

ENTRYPOINT [ "python3", "/start.py" ]