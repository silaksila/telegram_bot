# syntax=docker/dockerfile:1
FROM python:3.11
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]