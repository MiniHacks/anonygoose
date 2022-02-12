FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV PORT 8000
EXPOSE 8000

CMD ["python3", "-m", "rtmp_server"]
