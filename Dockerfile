FROM python:3

RUN apt-get update && apt-get -y install ffmpeg

RUN pip3 install Pillow

WORKDIR /code
CMD ["python", "mockBot.py"]
