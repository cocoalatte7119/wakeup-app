FROM python:3.9

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
