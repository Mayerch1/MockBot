FROM python:3

RUN pip3 install discord.py tinydb Pillow dblpy

WORKDIR /code
CMD ["python", "mockBot.py"]
