FROM python:3.9-slim-buster


WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV PORT 1935
EXPOSE 1935

CMD ["python3", "-m", "crack_two"]
